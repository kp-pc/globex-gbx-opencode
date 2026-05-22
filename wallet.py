import json
import os
import hashlib
import hmac
from typing import Optional

import ecdsa
from ecdsa import SigningKey, VerifyingKey, SECP256k1

import utils


WIF_VERSION_MAIN = 0x80
WIF_VERSION_TEST = 0xEF
PBKDF2_ITERATIONS = 200000
AES_KEY_SIZE = 32
IV_SIZE = 16
SALT_SIZE = 32
HMAC_KEY_SIZE = 32


class WalletError(Exception):
    pass


class Wallet:
    def __init__(self, private_key: bytes = None):
        if private_key:
            if len(private_key) != 32:
                raise WalletError("Private key must be 32 bytes")
            self.sk = SigningKey.from_string(private_key, curve=SECP256k1)
        else:
            self.sk = SigningKey.generate(curve=SECP256k1)
        self.vk = self.sk.verifying_key
        self.public_key = self.vk.to_string("compressed")
        self.address = utils.address_from_public_key(self.public_key)

    @property
    def private_key(self) -> bytes:
        return self.sk.to_string()

    def sign(self, message: bytes) -> bytes:
        return self.sk.sign(message)

    def sign_transaction(self, tx: dict) -> dict:
        signed_tx = {k: v for k, v in tx.items() if k != "signature"}
        signed_tx["public_key"] = self.public_key.hex()
        message = json.dumps(signed_tx, sort_keys=True).encode()
        signed_tx["signature"] = self.sign(message).hex()
        return signed_tx

    def to_dict(self) -> dict:
        return {
            "private_key": self.private_key.hex(),
            "public_key": self.public_key.hex(),
            "address": self.address
        }

    @classmethod
    def from_dict(cls, d: dict):
        return cls(private_key=bytes.fromhex(d["private_key"]))

    @staticmethod
    def verify_transaction(tx: dict) -> bool:
        if not tx.get("signature") or not tx.get("public_key"):
            return False
        expected_addr = utils.address_from_public_key(bytes.fromhex(tx["public_key"]))
        if expected_addr != tx.get("sender"):
            return False
        sig_bytes = bytes.fromhex(tx["signature"])
        pub_bytes = bytes.fromhex(tx["public_key"])
        verify_tx = {k: v for k, v in tx.items() if k != "signature"}
        message = json.dumps(verify_tx, sort_keys=True).encode()
        vk = VerifyingKey.from_string(pub_bytes, curve=SECP256k1)
        try:
            return vk.verify(sig_bytes, message)
        except ecdsa.BadSignatureError:
            return False

    # --- WIF (Wallet Import Format) ---

    def to_wif(self, compressed: bool = True, testnet: bool = False) -> str:
        version = WIF_VERSION_TEST if testnet else WIF_VERSION_MAIN
        data = self.private_key
        if compressed:
            data += b"\x01"
        return utils.base58_check_encode(data, version=version)

    @classmethod
    def from_wif(cls, wif: str) -> "Wallet":
        data = utils.base58_check_decode(wif)
        if len(data) not in (32, 33):
            raise WalletError("Invalid WIF key length")
        key_bytes = data[:32]
        return cls(private_key=key_bytes)

    # --- Encrypted Storage (AES-256-CBC + PBKDF2) ---

    @staticmethod
    def _derive_keys(password: str, salt: bytes) -> tuple[bytes, bytes]:
        raw = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt,
            PBKDF2_ITERATIONS, dklen=AES_KEY_SIZE + HMAC_KEY_SIZE
        )
        return raw[:AES_KEY_SIZE], raw[AES_KEY_SIZE:]

    def to_encrypted_dict(self, password: str) -> dict:
        from Crypto.Cipher import AES
        salt = os.urandom(SALT_SIZE)
        iv = os.urandom(IV_SIZE)
        enc_key, hmac_key = self._derive_keys(password, salt)
        cipher = AES.new(enc_key, AES.MODE_CBC, iv)
        plaintext = self.private_key
        pad_len = AES.block_size - (len(plaintext) % AES.block_size)
        plaintext += bytes([pad_len]) * pad_len
        ciphertext = cipher.encrypt(plaintext)
        payload = salt + iv + ciphertext
        mac = hmac.new(hmac_key, payload, hashlib.sha256).digest()
        return {
            "encrypted": True,
            "version": 1,
            "salt": salt.hex(),
            "iv": iv.hex(),
            "ciphertext": ciphertext.hex(),
            "mac": mac.hex(),
            "public_key": self.public_key.hex(),
            "address": self.address,
            "iterations": PBKDF2_ITERATIONS
        }

    @classmethod
    def from_encrypted_dict(cls, d: dict, password: str) -> "Wallet":
        from Crypto.Cipher import AES
        salt = bytes.fromhex(d["salt"])
        iv = bytes.fromhex(d["iv"])
        ciphertext = bytes.fromhex(d["ciphertext"])
        stored_mac = bytes.fromhex(d["mac"])
        enc_key, hmac_key = cls._derive_keys(password, salt)
        payload = salt + iv + ciphertext
        expected_mac = hmac.new(hmac_key, payload, hashlib.sha256).digest()
        if not hmac.compare_digest(expected_mac, stored_mac):
            raise WalletError("Invalid password or corrupted wallet")
        cipher = AES.new(enc_key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext)
        pad_len = plaintext[-1]
        if pad_len < 1 or pad_len > AES.block_size:
            raise WalletError("Decryption failed")
        plaintext = plaintext[:-pad_len]
        return cls(private_key=plaintext)

    # --- File operations ---

    def save(self, path: str, password: Optional[str] = None):
        if password:
            data = self.to_encrypted_dict(password)
        else:
            data = self.to_dict()
            data["encrypted"] = False
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path: str, password: Optional[str] = None) -> "Wallet":
        with open(path) as f:
            data = json.load(f)
        if data.get("encrypted"):
            if not password:
                raise WalletError("Wallet is encrypted, password required")
            return cls.from_encrypted_dict(data, password)
        return cls.from_dict(data)

    # --- Seed phrase (BIP39-style) ---

    @staticmethod
    def _load_wordlist() -> list[str]:
        return _BIP39_WORDS

    @classmethod
    def from_seed_phrase(cls, phrase: str, passphrase: str = "") -> "Wallet":
        words = phrase.strip().split()
        if len(words) not in (12, 15, 18, 21, 24):
            raise WalletError("Seed phrase must be 12, 15, 18, 21, or 24 words")
        mnemonic = " ".join(words)
        seed = hashlib.pbkdf2_hmac(
            "sha512", mnemonic.encode("utf-8"),
            b"mnemonic" + passphrase.encode("utf-8"),
            2048, dklen=64
        )
        return cls(private_key=seed[:32])

    def to_seed_phrase(self, word_count: int = 12) -> str:
        if word_count not in (12, 15, 18, 21, 24):
            raise WalletError("Word count must be 12, 15, 18, 21, or 24")
        entropy_bytes = word_count * 4 // 3
        entropy = os.urandom(entropy_bytes)
        wordlist = self._load_wordlist()
        entropy_bits = bin(int.from_bytes(entropy, "big"))[2:].zfill(entropy_bytes * 8)
        checksum = hashlib.sha256(entropy).digest()[0]
        checksum_bits = bin(checksum)[2:].zfill(8)[:entropy_bytes // 4]
        full_bits = entropy_bits + checksum_bits
        words = []
        for i in range(0, len(full_bits), 11):
            idx = int(full_bits[i:i + 11], 2)
            words.append(wordlist[idx])
        seed = hashlib.pbkdf2_hmac(
            "sha512", " ".join(words).encode("utf-8"),
            b"mnemonic", 2048, dklen=64
        )
        self.sk = SigningKey.from_string(seed[:32], curve=SECP256k1)
        self.vk = self.sk.verifying_key
        self.public_key = self.vk.to_string("compressed")
        self.address = utils.address_from_public_key(self.public_key)
        return " ".join(words)


def create_transaction(sender: str, recipient: str, amount: int,
                       fee: int = 0, nonce: int = 0) -> dict:
    return {
        "sender": sender,
        "recipient": recipient,
        "amount": amount,
        "fee": fee,
        "timestamp": __import__("time").time(),
        "nonce": nonce,
        "public_key": "",
        "signature": ""
    }


_BIP39_WORDS = [
    "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract", "absurd", "abuse",
    "access", "accident", "account", "accuse", "achieve", "acid", "acoustic", "acquire", "across", "act",
    "action", "actor", "actress", "actual", "adapt", "add", "addict", "address", "adjust", "admit",
    "adult", "advance", "advice", "aerobic", "affair", "afford", "afraid", "again", "age", "agent",
    "agree", "ahead", "aim", "air", "airport", "aisle", "alarm", "album", "alcohol", "alert",
    "alien", "all", "alley", "allow", "almost", "alone", "alpha", "already", "also", "alter",
    "always", "amateur", "amazing", "among", "amount", "amused", "analyst", "anchor", "ancient", "anger",
    "angle", "angry", "animal", "ankle", "announce", "annual", "another", "answer", "antenna", "antique",
    "anxiety", "any", "apart", "apology", "appear", "apple", "approve", "april", "arch", "arctic",
    "area", "arena", "argue", "arm", "armed", "armor", "army", "around", "arrange", "arrest",
    "arrive", "arrow", "art", "artifact", "artist", "artwork", "ask", "aspect", "assault", "asset",
    "assist", "assume", "asthma", "athlete", "atom", "attack", "attend", "attitude", "attract", "auction",
    "audit", "august", "aunt", "author", "auto", "autumn", "average", "avocado", "avoid", "awake",
    "aware", "away", "awesome", "awful", "awkward", "axis", "baby", "bachelor", "bacon", "badge",
    "bag", "balance", "balcony", "ball", "bamboo", "banana", "banner", "bar", "barely", "bargain",
    "barrel", "base", "basic", "basket", "battle", "beach", "bean", "beauty", "because", "become",
    "beef", "before", "begin", "behave", "behind", "believe", "below", "belt", "bench", "benefit",
    "best", "betray", "better", "between", "beyond", "bicycle", "bid", "bike", "bind", "biology",
    "bird", "birth", "bitter", "black", "blade", "blame", "blanket", "blast", "bleak", "bless",
    "blind", "blood", "blossom", "blouse", "blue", "blur", "blush", "board", "boat", "body",
    "boil", "bomb", "bone", "bonus", "book", "boost", "border", "boring", "borrow", "boss",
    "bottom", "bounce", "box", "boy", "bracket", "brain", "brand", "brass", "brave", "bread",
    "breeze", "brick", "bridge", "brief", "bright", "bring", "brisk", "broccoli", "broken", "bronze",
    "broom", "brother", "brown", "brush", "bubble", "buddy", "budget", "buffalo", "build", "bulb",
    "bulk", "bullet", "bundle", "bunker", "burden", "burger", "burst", "bus", "business", "busy",
    "butter", "buyer", "buzz", "cabbage", "cabin", "cable", "cactus", "cage", "cake", "call",
    "calm", "camera", "camp", "can", "canal", "cancel", "candle", "candy", "cannon", "canoe",
    "canvas", "canyon", "capable", "capital", "captain", "car", "carbon", "card", "cargo", "carpet",
    "carry", "cart", "case", "cash", "casino", "castle", "casual", "cat", "catalog", "catch",
    "category", "cattle", "caught", "cause", "caution", "cave", "ceiling", "celery", "cement", "census",
    "century", "cereal", "certain", "chair", "chalk", "champion", "change", "chaos", "chapter", "charge",
    "chase", "chat", "cheap", "check", "cheese", "chef", "cherry", "chest", "chicken", "chief",
    "child", "chimney", "choice", "choose", "chronic", "chuckle", "chunk", "churn", "cigar", "cinnamon",
    "circle", "citizen", "city", "civil", "claim", "clap", "clarify", "claw", "clay", "clean",
    "clerk", "clever", "click", "client", "cliff", "climb", "clinic", "clip", "clock", "clog",
    "close", "cloth", "cloud", "clown", "club", "clump", "cluster", "clutch", "coach", "coast",
    "coconut", "code", "coffee", "coil", "coin", "collect", "color", "column", "combine", "come",
    "comfort", "comic", "common", "company", "concert", "conduct", "confirm", "congress", "connect", "consider",
    "control", "convince", "cook", "cool", "copper", "copy", "coral", "core", "corn", "correct",
    "cost", "cotton", "couch", "country", "couple", "course", "cousin", "cover", "coyote", "crack",
    "cradle", "craft", "cram", "crane", "crash", "crater", "crawl", "crazy", "cream", "credit",
    "creek", "crew", "cricket", "crime", "crisp", "critic", "crop", "cross", "crouch", "crowd",
    "crucial", "cruel", "cruise", "crumble", "crunch", "crush", "cry", "crystal", "cube", "culture",
    "cup", "cupboard", "curious", "current", "curtain", "curve", "cushion", "custom", "cute", "cycle",
    "dad", "damage", "damp", "dance", "danger", "daring", "dash", "daughter", "dawn", "day",
    "deal", "debate", "debris", "decade", "december", "decide", "decline", "decorate", "decrease", "deer",
    "defense", "define", "defy", "degree", "delay", "deliver", "demand", "demise", "denial", "dentist",
    "deny", "depart", "depend", "deposit", "depth", "deputy", "derive", "describe", "desert", "design",
    "desk", "despair", "destroy", "detail", "detect", "develop", "device", "devote", "diagram", "dial",
    "diamond", "diary", "dice", "diesel", "diet", "differ", "digital", "dignity", "dilemma", "dinner",
    "dinosaur", "direct", "dirt", "disagree", "discover", "disease", "dish", "dismiss", "disorder", "display",
    "distance", "divert", "divide", "divorce", "dizzy", "doctor", "document", "dog", "doll", "dolphin",
    "domain", "donate", "donkey", "donor", "door", "dose", "double", "dove", "draft", "dragon",
    "drama", "drastic", "draw", "dream", "dress", "drift", "drill", "drink", "drip", "drive",
    "drop", "drum", "dry", "duck", "dumb", "dune", "during", "dust", "dutch", "duty",
    "dwarf", "dynamic", "eager", "eagle", "early", "earn", "earth", "easily", "east", "easy",
    "echo", "ecology", "economy", "edge", "edit", "educate", "effort", "egg", "eight", "either",
    "elbow", "elder", "electric", "elegant", "element", "elephant", "elevator", "elite", "else", "embark",
    "embody", "embrace", "emerge", "emotion", "employ", "empower", "empty", "enable", "enact", "end",
    "endless", "endorse", "enemy", "energy", "enforce", "engage", "engine", "enhance", "enjoy", "enlist",
    "enough", "enrich", "enroll", "ensure", "enter", "entire", "entry", "envelope", "episode", "equal",
    "equip", "era", "erase", "erode", "erosion", "error", "erupt", "escape", "essay", "essence",
    "estate", "eternal", "ethics", "evidence", "evil", "evoke", "evolve", "exact", "example", "excess",
    "exchange", "excite", "exclude", "excuse", "execute", "exercise", "exhaust", "exhibit", "exile", "exist",
    "exit", "exotic", "expand", "expect", "expire", "explain", "expose", "express", "extend", "extra",
    "eye", "eyebrow", "fabric", "face", "faculty", "fade", "faint", "faith", "fall", "false",
    "fame", "family", "famous", "fan", "fancy", "fantasy", "farm", "fashion", "fat", "fatal",
    "father", "fatigue", "fault", "favorite", "feature", "february", "federal", "fee", "feed", "feel",
    "female", "fence", "festival", "fetch", "fever", "few", "fiber", "fiction", "field", "figure",
    "file", "film", "filter", "final", "find", "fine", "finger", "finish", "fire", "firm",
    "first", "fiscal", "fish", "fit", "fitness", "fix", "flag", "flame", "flash", "flat",
    "flavor", "flee", "flight", "flip", "float", "flock", "floor", "flower", "fluid", "flush",
    "fly", "foam", "focus", "fog", "foil", "fold", "follow", "food", "foot", "force",
    "foreign", "forest", "forget", "fork", "fortune", "forum", "forward", "fossil", "foster", "found",
    "fox", "fragile", "frame", "frequent", "fresh", "friend", "fringe", "frog", "front", "frost",
    "frown", "frozen", "fruit", "fuel", "fun", "funny", "furnace", "fury", "future", "gadget",
    "gain", "galaxy", "gallery", "game", "gap", "garage", "garbage", "garden", "garlic", "garment",
    "gas", "gasp", "gate", "gather", "gauge", "gaze", "general", "genius", "genre", "gentle",
    "genuine", "gesture", "ghost", "giant", "gift", "giggle", "ginger", "giraffe", "girl", "give",
    "glad", "glance", "glare", "glass", "glide", "glimpse", "globe", "gloom", "glory", "glove",
    "glow", "glue", "goat", "goddess", "gold", "good", "goose", "gorilla", "gospel", "gossip",
    "govern", "gown", "grab", "grace", "grain", "grant", "grape", "grass", "gravity", "great",
    "green", "grid", "grief", "grit", "grocery", "group", "grow", "grunt", "guard", "guess",
    "guide", "guilt", "guitar", "gun", "gym", "habit", "hair", "half", "hammer", "hamster",
    "hand", "happy", "harbor", "hard", "harsh", "harvest", "hat", "have", "hawk", "hazard",
    "head", "health", "heart", "heavy", "hedgehog", "height", "hello", "helmet", "help", "hen",
    "hero", "hidden", "high", "hill", "hint", "hip", "hire", "history", "hobby", "hockey",
    "hold", "hole", "holiday", "hollow", "home", "honey", "hood", "hope", "horn", "horror",
    "horse", "hospital", "host", "hotel", "hour", "hover", "hub", "huge", "human", "humble",
    "humor", "hundred", "hungry", "hunt", "hurdle", "hurry", "hurt", "husband", "hybrid", "ice",
    "icon", "idea", "identify", "idle", "ignore", "ill", "illegal", "illness", "image", "imitate",
    "immense", "immune", "impact", "impose", "improve", "impulse", "inch", "include", "income", "increase",
    "index", "indicate", "indoor", "industry", "infant", "inflict", "inform", "inhale", "inherit", "initial",
    "inject", "injury", "inmate", "inner", "innocent", "input", "inquiry", "insane", "insect", "inside",
    "inspire", "install", "intact", "interest", "into", "invest", "invite", "involve", "iron", "island",
    "isolate", "issue", "item", "ivory", "jacket", "jaguar", "jar", "jazz", "jealous", "jeans",
    "jelly", "jewel", "job", "join", "joke", "journey", "joy", "judge", "juice", "jump",
    "jungle", "junior", "junk", "just", "kangaroo", "keen", "keep", "ketchup", "key", "kick",
    "kid", "kidney", "kind", "kingdom", "kiss", "kit", "kitchen", "kite", "kitten", "kiwi",
    "knee", "knife", "knock", "know", "lab", "label", "labor", "ladder", "lady", "lake",
    "lamp", "language", "laptop", "large", "later", "latin", "laugh", "laundry", "lava", "law",
    "lawn", "lawsuit", "layer", "lazy", "leader", "leaf", "learn", "leave", "lecture", "left",
    "leg", "legal", "legend", "leisure", "lemon", "lend", "length", "lens", "leopard", "lesson",
    "letter", "level", "liar", "liberty", "library", "license", "life", "lift", "light", "like",
    "limb", "limit", "link", "lion", "liquid", "list", "little", "live", "lizard", "load",
    "loan", "lobster", "local", "lock", "logic", "lonely", "long", "loop", "lottery", "loud",
    "lounge", "love", "loyal", "lucky", "luggage", "lumber", "lunar", "lunch", "luxury", "lyrics",
    "machine", "mad", "magic", "magnet", "maid", "mail", "main", "major", "make", "mammal",
    "man", "manage", "mandate", "mango", "mansion", "manual", "maple", "marble", "march", "margin",
    "marine", "market", "marriage", "mask", "mass", "master", "match", "material", "math", "matrix",
    "matter", "maximum", "maze", "meadow", "mean", "measure", "meat", "mechanic", "medal", "media",
    "melody", "melt", "member", "memory", "mention", "menu", "mercy", "merge", "merit", "merry",
    "mesh", "message", "metal", "method", "middle", "midnight", "milk", "million", "mimic", "mind",
    "minimum", "minor", "minute", "miracle", "mirror", "misery", "miss", "mistake", "mix", "mixed",
    "mixture", "mobile", "model", "modify", "mom", "moment", "monitor", "monkey", "monster", "month",
    "moon", "moral", "more", "morning", "mosquito", "mother", "motion", "motor", "mountain", "mouse",
    "move", "movie", "much", "muffin", "mule", "multiply", "muscle", "museum", "mushroom", "music",
    "must", "mutual", "myself", "mystery", "myth", "naive", "name", "napkin", "narrow", "nasty",
    "nation", "nature", "near", "neck", "need", "negative", "neglect", "neither", "nephew", "nerve",
    "nest", "net", "network", "neutral", "never", "news", "next", "nice", "night", "noble",
    "noise", "nominee", "noodle", "normal", "north", "nose", "notable", "note", "nothing", "notice",
    "novel", "now", "nuclear", "number", "nurse", "nut", "oak", "obey", "object", "oblige",
    "obscure", "observe", "obtain", "obvious", "occur", "ocean", "october", "odor", "off", "offend",
    "offer", "office", "often", "oil", "okay", "old", "olive", "olympic", "omit", "once",
    "one", "onion", "online", "only", "open", "opera", "opinion", "oppose", "option", "orange",
    "orbit", "orchard", "order", "ordinary", "organ", "orient", "original", "orphan", "ostrich", "other",
    "outdoor", "outer", "output", "outside", "oval", "oven", "over", "own", "owner", "oxygen",
    "oyster", "ozone", "pact", "paddle", "page", "pair", "palace", "palm", "panda", "panel",
    "panic", "panther", "paper", "parade", "parent", "park", "parrot", "party", "pass", "patch",
    "path", "patient", "patrol", "pattern", "pause", "pave", "payment", "peace", "peanut", "pear",
    "peasant", "pelican", "pen", "penalty", "pencil", "people", "pepper", "perfect", "permit", "person",
    "pet", "phone", "photo", "phrase", "physical", "piano", "picnic", "picture", "piece", "pig",
    "pigeon", "pill", "pilot", "pink", "pioneer", "pipe", "pistol", "pitch", "pizza", "place",
    "planet", "plastic", "plate", "play", "player", "playground", "pleasure", "pledge", "pluck", "plug",
    "plunge", "poem", "poet", "point", "polar", "pole", "police", "pond", "pony", "pool",
    "popular", "portion", "position", "possible", "post", "potato", "pottery", "poverty", "powder", "power",
    "practice", "praise", "predict", "prefer", "prepare", "present", "pretty", "prevent", "price", "pride",
    "primary", "print", "priority", "prison", "private", "prize", "problem", "process", "produce", "profit",
    "program", "project", "promote", "proof", "property", "prosper", "protect", "proud", "provide", "public",
    "pudding", "pull", "pulp", "pulse", "pumpkin", "punch", "pupil", "puppy", "purchase", "purity",
    "purpose", "purse", "push", "put", "puzzle", "pyramid", "quality", "quantum", "quarter", "question",
    "quick", "quit", "quiz", "quote", "rabbit", "raccoon", "race", "rack", "radar", "radio",
    "rail", "rain", "raise", "rally", "ramp", "ranch", "random", "range", "rapid", "rare",
    "rate", "rather", "raven", "raw", "razor", "ready", "real", "reason", "rebel", "rebuild",
    "recall", "receive", "recipe", "record", "recycle", "reduce", "reflect", "reform", "refuse", "region",
    "regret", "regular", "reject", "relax", "release", "relief", "rely", "remain", "remember", "remind",
    "remove", "render", "renew", "rent", "reopen", "repair", "repeat", "replace", "report", "require",
    "rescue", "resemble", "resist", "resource", "response", "result", "retire", "retreat", "return", "reunion",
    "reveal", "review", "reward", "rhythm", "rib", "ribbon", "rice", "rich", "ride", "ridge",
    "rifle", "right", "rigid", "ring", "riot", "ripple", "risk", "ritual", "rival", "river",
    "road", "roast", "robot", "robust", "rocket", "romance", "roof", "rookie", "room", "rose",
    "rotate", "rough", "round", "route", "royal", "rubber", "rude", "rug", "rule", "run",
    "runway", "rural", "sad", "saddle", "sadness", "safe", "sail", "salad", "salmon", "salon",
    "salt", "salute", "same", "sample", "sand", "satisfy", "satoshi", "sauce", "sausage", "save",
    "say", "scale", "scan", "scare", "scatter", "scene", "scheme", "school", "science", "scissors",
    "scorpion", "scout", "scrap", "screen", "script", "scrub", "sea", "search", "season", "seat",
    "second", "secret", "section", "security", "seed", "seek", "segment", "select", "sell", "seminar",
    "senior", "sense", "sentence", "series", "service", "session", "settle", "setup", "seven", "shadow",
    "shaft", "shallow", "share", "shed", "shell", "sheriff", "shield", "shift", "shine", "ship",
    "shiver", "shock", "shoe", "shoot", "shop", "short", "shoulder", "shove", "shrimp", "shrug",
    "shuffle", "shy", "sibling", "sick", "side", "siege", "sight", "sign", "silent", "silk",
    "silly", "silver", "similar", "simple", "since", "sing", "siren", "sister", "situate", "six",
    "size", "skate", "sketch", "ski", "skill", "skin", "skirt", "skull", "slab", "slam",
    "sleep", "slender", "slice", "slide", "slight", "slim", "slogan", "slot", "slow", "slush",
    "small", "smart", "smile", "smoke", "smooth", "snack", "snake", "snap", "sniff", "snow",
    "soap", "soccer", "social", "sock", "soda", "soft", "solar", "soldier", "solid", "solution",
    "solve", "someone", "song", "soon", "sorry", "sort", "soul", "sound", "soup", "source",
    "south", "space", "spare", "spatial", "spawn", "speak", "special", "speed", "spell", "spend",
    "sphere", "spice", "spider", "spike", "spin", "spirit", "split", "spoil", "sponsor", "spoon",
    "sport", "spot", "spray", "spread", "spring", "spy", "square", "squeeze", "squirrel", "stable",
    "stadium", "staff", "stage", "stairs", "stamp", "stand", "start", "state", "stay", "steak",
    "steel", "step", "stereo", "stick", "still", "sting", "stock", "stomach", "stone", "stool",
    "story", "stove", "strategy", "street", "strike", "strong", "struggle", "student", "stuff", "stumble",
    "style", "subject", "submit", "subway", "success", "such", "sudden", "suffer", "sugar", "suggest",
    "suit", "sun", "sunny", "sunset", "super", "supply", "support", "suppose", "sure", "surface",
    "surge", "surprise", "surround", "survey", "suspect", "sustain", "swallow", "swamp", "swap", "swarm",
    "swear", "sweet", "swift", "swim", "swing", "switch", "sword", "symbol", "symptom", "syrup",
    "system", "table", "tackle", "tag", "tail", "talent", "talk", "tank", "tape", "target",
    "task", "taste", "tattoo", "taxi", "teach", "team", "tell", "ten", "tenant", "tennis",
    "tent", "term", "test", "text", "thank", "that", "theme", "then", "theory", "there",
    "they", "thing", "this", "thought", "three", "thrive", "throw", "thumb", "thunder", "ticket",
    "tide", "tiger", "tilt", "timber", "time", "tiny", "tip", "tired", "tissue", "title",
    "toast", "tobacco", "today", "toddler", "toe", "together", "toilet", "token", "tomato", "tomorrow",
    "tone", "tongue", "tonight", "tool", "tooth", "top", "topic", "topple", "torch", "tornado",
    "tortoise", "toss", "total", "tourist", "toward", "tower", "town", "toy", "track", "trade",
    "traffic", "tragic", "train", "transfer", "trap", "trash", "travel", "tray", "treat", "tree",
    "trend", "trial", "tribe", "trick", "trigger", "trim", "trip", "trophy", "trouble", "truck",
    "true", "truly", "trumpet", "trust", "truth", "try", "tube", "tuition", "tumble", "tuna",
    "tunnel", "turkey", "turn", "turtle", "twelve", "twenty", "twice", "twin", "twist", "two",
    "type", "typical", "ugly", "umbrella", "unable", "unaware", "uncle", "uncover", "under", "undo",
    "unfair", "unfold", "unhappy", "uniform", "unique", "unit", "universe", "unknown", "unlock", "until",
    "unusual", "unveil", "update", "upgrade", "uphold", "upon", "upper", "upset", "urban", "urge",
    "usage", "use", "used", "useful", "useless", "usual", "utility", "vacant", "vacuum", "vague",
    "valid", "valley", "valve", "van", "vanish", "vapor", "various", "vast", "vault", "vehicle",
    "velvet", "vendor", "venture", "venue", "verb", "verify", "version", "very", "vessel", "veteran",
    "viable", "vibrant", "vicious", "victory", "video", "view", "village", "vintage", "violin", "virtual",
    "virus", "visa", "visit", "visual", "vital", "vivid", "vocal", "voice", "void", "volcano",
    "volume", "vote", "voyage", "wage", "wagon", "wait", "walk", "wall", "walnut", "want",
    "warfare", "warm", "warrior", "wash", "wasp", "waste", "water", "wave", "way", "wealth",
    "weapon", "wear", "weasel", "weather", "web", "wedding", "weekend", "weird", "welcome", "west",
    "wet", "whale", "what", "wheat", "wheel", "when", "where", "whip", "whisper", "wide",
    "width", "wife", "wild", "will", "win", "window", "wine", "wing", "wink", "winner",
    "winter", "wire", "wisdom", "wise", "wish", "witness", "wolf", "woman", "wonder", "wood",
    "wool", "word", "work", "world", "worry", "worth", "wrap", "wreck", "wrestle", "wrist",
    "write", "wrong", "yard", "year", "yellow", "you", "young", "youth", "zebra", "zero",
    "zone", "zoo"
]
