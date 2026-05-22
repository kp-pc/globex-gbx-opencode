import json
import os
import time
import struct
import hashlib
import hmac
import secrets
from typing import Optional, Tuple, List, Union
from enum import Enum

import ecdsa
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from ecdsa.util import sigencode_der, sigdecode_der

import utils
import config


BIP39_WORDLIST = [
'abandon', 'ability', 'able', 'about', 'above', 'absent', 'absorb', 'abstract', 'absurd', 'abuse', 'access'
, 'accident', 'account', 'accuse', 'achieve', 'acid', 'acoustic', 'acquire', 'across', 'act', 'action'
, 'actor', 'actress', 'actual', 'adapt', 'add', 'addict', 'address', 'adjust', 'admit', 'adult', 'advance'
, 'advice', 'aerobic', 'affair', 'afford', 'afraid', 'again', 'age', 'agent', 'agree', 'ahead', 'aim'
, 'air', 'airport', 'aisle', 'alarm', 'album', 'alcohol', 'alert', 'alien', 'all', 'alley', 'allow', 'almost'
, 'alone', 'alpha', 'already', 'also', 'alter', 'always', 'amateur', 'amazing', 'among', 'amount', 'amused'
, 'analyst', 'anchor', 'ancient', 'anger', 'angle', 'angry', 'animal', 'ankle', 'announce', 'annual', 'another'
, 'answer', 'antenna', 'antique', 'anxiety', 'any', 'apart', 'apology', 'appear', 'apple', 'approve', 'april'
, 'arch', 'arctic', 'area', 'arena', 'argue', 'arm', 'armed', 'armor', 'army', 'around', 'arrange', 'arrest'
, 'arrive', 'arrow', 'art', 'artefact', 'artist', 'artwork', 'ask', 'aspect', 'assault', 'asset', 'assist'
, 'assume', 'asthma', 'athlete', 'atom', 'attack', 'attend', 'attitude', 'attract', 'auction', 'audit'
, 'august', 'aunt', 'author', 'auto', 'autumn', 'average', 'avocado', 'avoid', 'awake', 'aware', 'away'
, 'awesome', 'awful', 'awkward', 'axis', 'baby', 'bachelor', 'bacon', 'badge', 'bag', 'balance', 'balcony'
, 'ball', 'bamboo', 'banana', 'banner', 'bar', 'barely', 'bargain', 'barrel', 'base', 'basic', 'basket'
, 'battle', 'beach', 'bean', 'beauty', 'because', 'become', 'beef', 'before', 'begin', 'behave', 'behind'
, 'believe', 'below', 'belt', 'bench', 'benefit', 'best', 'betray', 'better', 'between', 'beyond', 'bicycle'
, 'bid', 'bike', 'bind', 'biology', 'bird', 'birth', 'bitter', 'black', 'blade', 'blame', 'blanket', 'blast'
, 'bleak', 'bless', 'blind', 'blood', 'blossom', 'blouse', 'blue', 'blur', 'blush', 'board', 'boat', 'body'
, 'boil', 'bomb', 'bone', 'bonus', 'book', 'boost', 'border', 'boring', 'borrow', 'boss', 'bottom', 'bounce'
, 'box', 'boy', 'bracket', 'brain', 'brand', 'brass', 'brave', 'bread', 'breeze', 'brick', 'bridge', 'brief'
, 'bright', 'bring', 'brisk', 'broccoli', 'broken', 'bronze', 'broom', 'brother', 'brown', 'brush', 'bubble'
, 'buddy', 'budget', 'buffalo', 'build', 'bulb', 'bulk', 'bullet', 'bundle', 'bunker', 'burden', 'burger'
, 'burst', 'bus', 'business', 'busy', 'butter', 'buyer', 'buzz', 'cabbage', 'cabin', 'cable', 'cactus'
, 'cage', 'cake', 'call', 'calm', 'camera', 'camp', 'can', 'canal', 'cancel', 'candy', 'cannon', 'canoe'
, 'canvas', 'canyon', 'capable', 'capital', 'captain', 'car', 'carbon', 'card', 'cargo', 'carpet', 'carry'
, 'cart', 'case', 'cash', 'casino', 'castle', 'casual', 'cat', 'catalog', 'catch', 'category', 'cattle'
, 'caught', 'cause', 'caution', 'cave', 'ceiling', 'celery', 'cement', 'census', 'century', 'cereal', 'certain'
, 'chair', 'chalk', 'champion', 'change', 'chaos', 'chapter', 'charge', 'chase', 'chat', 'cheap', 'check'
, 'cheese', 'chef', 'cherry', 'chest', 'chicken', 'chief', 'child', 'chimney', 'choice', 'choose', 'chronic'
, 'chuckle', 'chunk', 'churn', 'cigar', 'cinnamon', 'circle', 'citizen', 'city', 'civil', 'claim', 'clap'
, 'clarify', 'claw', 'clay', 'clean', 'clerk', 'clever', 'click', 'client', 'cliff', 'climb', 'clinic'
, 'clip', 'clock', 'clog', 'close', 'cloth', 'cloud', 'clown', 'club', 'clump', 'cluster', 'clutch', 'coach'
, 'coast', 'coconut', 'code', 'coffee', 'coil', 'coin', 'collect', 'color', 'column', 'combine', 'come'
, 'comfort', 'comic', 'common', 'company', 'concert', 'conduct', 'confirm', 'congress', 'connect', 'consider'
, 'control', 'convince', 'cook', 'cool', 'copper', 'copy', 'coral', 'core', 'corn', 'correct', 'cost'
, 'cotton', 'couch', 'country', 'couple', 'course', 'cousin', 'cover', 'coyote', 'crack', 'cradle', 'craft'
, 'cram', 'crane', 'crash', 'crater', 'crawl', 'crazy', 'cream', 'credit', 'creek', 'crew', 'cricket'
, 'crime', 'crisp', 'critic', 'crop', 'cross', 'crouch', 'crowd', 'crucial', 'cruel', 'cruise', 'crumble'
, 'crunch', 'crush', 'cry', 'crystal', 'cube', 'culture', 'cup', 'cupboard', 'curious', 'current', 'curtain'
, 'curve', 'cushion', 'custom', 'cute', 'cycle', 'dad', 'damage', 'damp', 'dance', 'danger', 'daring'
, 'dash', 'daughter', 'dawn', 'day', 'deal', 'debate', 'debris', 'decade', 'december', 'decide', 'decline'
, 'decorate', 'decrease', 'deer', 'defense', 'define', 'defy', 'degree', 'delay', 'deliver', 'demand'
, 'demise', 'denial', 'dentist', 'deny', 'depart', 'depend', 'deposit', 'depth', 'deputy', 'derive', 'describe'
, 'desert', 'design', 'desk', 'despair', 'destroy', 'detail', 'detect', 'develop', 'device', 'devote'
, 'diagram', 'dial', 'diamond', 'diary', 'dice', 'diesel', 'diet', 'differ', 'digital', 'dignity', 'dilemma'
, 'dinner', 'dinosaur', 'direct', 'dirt', 'disagree', 'discover', 'disease', 'dish', 'dismiss', 'disorder'
, 'display', 'distance', 'divert', 'divide', 'divorce', 'dizzy', 'doctor', 'document', 'dog', 'doll', 'dolphin'
, 'domain', 'donate', 'donkey', 'donor', 'door', 'dose', 'double', 'dove', 'draft', 'dragon', 'drama'
, 'drastic', 'draw', 'dream', 'dress', 'drift', 'drill', 'drink', 'drip', 'drive', 'drop', 'drum', 'dry'
, 'duck', 'dumb', 'dune', 'during', 'dust', 'dutch', 'duty', 'dwarf', 'dynamic', 'eager', 'eagle', 'early'
, 'earn', 'earth', 'easily', 'east', 'easy', 'echo', 'ecology', 'economy', 'edge', 'edit', 'educate', 'effort'
, 'egg', 'eight', 'either', 'elbow', 'elder', 'electric', 'elegant', 'element', 'elephant', 'elevator'
, 'elite', 'else', 'embark', 'embody', 'embrace', 'emerge', 'emotion', 'employ', 'empower', 'empty', 'enable'
, 'enact', 'end', 'endless', 'endorse', 'enemy', 'energy', 'enforce', 'engage', 'engine', 'enhance', 'enjoy'
, 'enlist', 'enough', 'enrich', 'enroll', 'ensure', 'enter', 'entire', 'entry', 'envelope', 'episode'
, 'equal', 'equip', 'era', 'erase', 'erode', 'erosion', 'error', 'erupt', 'escape', 'essay', 'essence'
, 'estate', 'eternal', 'ethics', 'evidence', 'evil', 'evoke', 'evolve', 'exact', 'example', 'excess', 'exchange'
, 'excite', 'exclude', 'excuse', 'execute', 'exercise', 'exhaust', 'exhibit', 'exile', 'exist', 'exit'
, 'exotic', 'expand', 'expect', 'expire', 'explain', 'expose', 'express', 'extend', 'extra', 'eye', 'eyebrow'
, 'fabric', 'face', 'faculty', 'fade', 'faint', 'faith', 'fall', 'false', 'fame', 'family', 'famous', 'fan'
, 'fancy', 'fantasy', 'farm', 'fashion', 'fat', 'fatal', 'father', 'fatigue', 'fault', 'favorite', 'feature'
, 'february', 'federal', 'fee', 'feed', 'feel', 'female', 'fence', 'festival', 'fetch', 'fever', 'few'
, 'fiber', 'fiction', 'field', 'figure', 'file', 'film', 'filter', 'final', 'find', 'fine', 'finger', 'finish'
, 'fire', 'firm', 'first', 'fiscal', 'fish', 'fit', 'fitness', 'fix', 'flag', 'flame', 'flash', 'flat'
, 'flavor', 'flee', 'flight', 'flip', 'float', 'flock', 'floor', 'flower', 'fluid', 'flush', 'fly', 'foam'
, 'focus', 'fog', 'foil', 'fold', 'follow', 'food', 'foot', 'force', 'forest', 'forget', 'fork', 'fortune'
, 'forum', 'forward', 'fossil', 'foster', 'found', 'fox', 'fragile', 'frame', 'frequent', 'fresh', 'friend'
, 'fringe', 'frog', 'front', 'frost', 'frown', 'frozen', 'fruit', 'fuel', 'fun', 'funny', 'furnace', 'fury'
, 'future', 'gadget', 'gain', 'galaxy', 'gallery', 'game', 'gap', 'garage', 'garbage', 'garden', 'garlic'
, 'garment', 'gas', 'gasp', 'gate', 'gather', 'gauge', 'gaze', 'general', 'genius', 'genre', 'gentle'
, 'genuine', 'gesture', 'ghost', 'giant', 'gift', 'giggle', 'ginger', 'giraffe', 'girl', 'give', 'glad'
, 'glance', 'glare', 'glass', 'glide', 'glimpse', 'globe', 'gloom', 'glory', 'glove', 'glow', 'glue', 'goat'
, 'goddess', 'gold', 'good', 'goose', 'gorilla', 'gospel', 'gossip', 'govern', 'gown', 'grab', 'grace'
, 'grain', 'grant', 'grape', 'grass', 'gravity', 'great', 'green', 'grid', 'grief', 'grit', 'grocery'
, 'group', 'grow', 'grunt', 'guard', 'guess', 'guide', 'guilt', 'guitar', 'gun', 'gym', 'habit', 'hair'
, 'half', 'hammer', 'hamster', 'hand', 'happy', 'harbor', 'hard', 'harsh', 'harvest', 'hat', 'have', 'hawk'
, 'hazard', 'head', 'health', 'heart', 'heavy', 'hedgehog', 'height', 'hello', 'helmet', 'help', 'hen'
, 'hero', 'hidden', 'high', 'hill', 'hint', 'hip', 'hire', 'history', 'hobby', 'hockey', 'hold', 'hole'
, 'holiday', 'hollow', 'home', 'honey', 'hood', 'hope', 'horn', 'horror', 'horse', 'hospital', 'host'
, 'hotel', 'hour', 'hover', 'hub', 'huge', 'human', 'humble', 'humor', 'hundred', 'hungry', 'hunt', 'hurdle'
, 'hurry', 'hurt', 'husband', 'hybrid', 'ice', 'icon', 'idea', 'identify', 'idle', 'ignore', 'ill', 'illegal'
, 'illness', 'image', 'imitate', 'immense', 'immune', 'impact', 'impose', 'improve', 'impulse', 'inch'
, 'include', 'income', 'increase', 'index', 'indicate', 'indoor', 'industry', 'infant', 'inflict', 'inform'
, 'inhale', 'inherit', 'initial', 'inject', 'injury', 'inmate', 'inner', 'innocent', 'input', 'inquiry'
, 'insane', 'insect', 'inside', 'inspire', 'install', 'intact', 'interest', 'into', 'invest', 'invite'
, 'involve', 'iron', 'island', 'isolate', 'issue', 'item', 'ivory', 'jacket', 'jaguar', 'jar', 'jazz'
, 'jealous', 'jeans', 'jelly', 'jewel', 'job', 'join', 'joke', 'journey', 'joy', 'judge', 'juice', 'jump'
, 'jungle', 'junior', 'junk', 'just', 'kangaroo', 'keen', 'keep', 'ketchup', 'key', 'kick', 'kid', 'kidney'
, 'kind', 'kingdom', 'kiss', 'kit', 'kitchen', 'kite', 'kitten', 'kiwi', 'knee', 'knife', 'knock', 'know'
, 'lab', 'label', 'labor', 'ladder', 'lady', 'lake', 'lamp', 'language', 'laptop', 'large', 'later', 'latin'
, 'laugh', 'laundry', 'lava', 'law', 'lawn', 'lawsuit', 'layer', 'lazy', 'leader', 'leaf', 'learn', 'leave'
, 'lecture', 'left', 'leg', 'legal', 'legend', 'leisure', 'lemon', 'lend', 'length', 'lens', 'leopard'
, 'lesson', 'letter', 'level', 'liar', 'liberty', 'library', 'license', 'life', 'lift', 'light', 'like'
, 'limb', 'limit', 'link', 'lion', 'liquid', 'list', 'little', 'live', 'lizard', 'load', 'loan', 'lobster'
, 'local', 'lock', 'logic', 'lonely', 'long', 'loop', 'lottery', 'loud', 'lounge', 'love', 'loyal', 'lucky'
, 'luggage', 'lumber', 'lunar', 'lunch', 'luxury', 'lyrics', 'machine', 'mad', 'magic', 'magnet', 'maid'
, 'mail', 'main', 'major', 'make', 'mammal', 'man', 'manage', 'mandate', 'mango', 'mansion', 'manual'
, 'maple', 'marble', 'march', 'margin', 'marine', 'market', 'marriage', 'mask', 'mass', 'master', 'match'
, 'material', 'math', 'matrix', 'matter', 'maximum', 'maze', 'meadow', 'mean', 'measure', 'meat', 'mechanic'
, 'medal', 'media', 'melody', 'melt', 'member', 'memory', 'mention', 'menu', 'mercy', 'merge', 'merit'
, 'merry', 'mesh', 'message', 'metal', 'method', 'middle', 'midnight', 'milk', 'million', 'mimic', 'mind'
, 'minimum', 'minor', 'minute', 'miracle', 'mirror', 'misery', 'miss', 'mistake', 'mix', 'mixed', 'mixture'
, 'mobile', 'model', 'modify', 'mom', 'moment', 'monitor', 'monkey', 'monster', 'month', 'moon', 'moral'
, 'more', 'morning', 'mosquito', 'mother', 'motion', 'motor', 'mountain', 'mouse', 'move', 'movie', 'much'
, 'muffin', 'mule', 'multiply', 'muscle', 'museum', 'mushroom', 'music', 'must', 'mutual', 'myself', 'mystery'
, 'myth', 'naive', 'name', 'napkin', 'narrow', 'nasty', 'nation', 'nature', 'near', 'neck', 'need', 'negative'
, 'neglect', 'neither', 'nephew', 'nerve', 'nest', 'net', 'network', 'neutral', 'never', 'news', 'next'
, 'nice', 'night', 'noble', 'noise', 'nominee', 'noodle', 'normal', 'north', 'nose', 'notable', 'note'
, 'nothing', 'notice', 'novel', 'now', 'nuclear', 'number', 'nurse', 'nut', 'oak', 'obey', 'object', 'oblige'
, 'obscure', 'observe', 'obtain', 'obvious', 'occur', 'ocean', 'october', 'odor', 'off', 'offer', 'office'
, 'often', 'oil', 'okay', 'old', 'olive', 'olympic', 'omit', 'once', 'one', 'onion', 'online', 'only'
, 'open', 'opera', 'opinion', 'oppose', 'option', 'orange', 'orbit', 'orchard', 'order', 'ordinary', 'organ'
, 'orient', 'original', 'orphan', 'ostrich', 'other', 'outdoor', 'outer', 'output', 'outside', 'oval'
, 'oven', 'over', 'own', 'owner', 'oxygen', 'oyster', 'ozone', 'pact', 'paddle', 'page', 'pair', 'palace'
, 'palm', 'panda', 'panel', 'panic', 'panther', 'paper', 'parade', 'parent', 'park', 'parrot', 'party'
, 'pass', 'patch', 'path', 'patient', 'patrol', 'pattern', 'pause', 'pave', 'payment', 'peace', 'peanut'
, 'pear', 'peasant', 'pelican', 'pen', 'penalty', 'pencil', 'people', 'pepper', 'perfect', 'permit', 'person'
, 'pet', 'phone', 'photo', 'phrase', 'physical', 'piano', 'picnic', 'picture', 'piece', 'pig', 'pigeon'
, 'pill', 'pilot', 'pink', 'pioneer', 'pipe', 'pistol', 'pitch', 'pizza', 'place', 'planet', 'plastic'
, 'plate', 'play', 'please', 'pledge', 'pluck', 'plug', 'plunge', 'poem', 'poet', 'point', 'polar', 'pole'
, 'police', 'pond', 'pony', 'pool', 'popular', 'portion', 'position', 'possible', 'post', 'potato', 'pottery'
, 'poverty', 'powder', 'power', 'practice', 'praise', 'predict', 'prefer', 'prepare', 'present', 'pretty'
, 'prevent', 'price', 'pride', 'primary', 'print', 'priority', 'prison', 'private', 'prize', 'problem'
, 'process', 'produce', 'profit', 'program', 'project', 'promote', 'proof', 'property', 'prosper', 'protect'
, 'proud', 'provide', 'public', 'pudding', 'pull', 'pulp', 'pulse', 'pumpkin', 'punch', 'pupil', 'puppy'
, 'purchase', 'purity', 'purpose', 'purse', 'push', 'put', 'puzzle', 'pyramid', 'quality', 'quantum', 'quarter'
, 'question', 'quick', 'quit', 'quiz', 'quote', 'rabbit', 'raccoon', 'race', 'rack', 'radar', 'radio'
, 'rail', 'rain', 'raise', 'rally', 'ramp', 'ranch', 'random', 'range', 'rapid', 'rare', 'rate', 'rather'
, 'raven', 'raw', 'razor', 'ready', 'real', 'reason', 'rebel', 'rebuild', 'recall', 'receive', 'recipe'
, 'record', 'recycle', 'reduce', 'reflect', 'reform', 'refuse', 'region', 'regret', 'regular', 'reject'
, 'relax', 'release', 'relief', 'rely', 'remain', 'remember', 'remind', 'remove', 'render', 'renew', 'rent'
, 'reopen', 'repair', 'repeat', 'replace', 'report', 'require', 'rescue', 'resemble', 'resist', 'resource'
, 'response', 'result', 'retire', 'retreat', 'return', 'reunion', 'reveal', 'review', 'reward', 'rhythm'
, 'rib', 'ribbon', 'rice', 'rich', 'ride', 'ridge', 'rifle', 'right', 'rigid', 'ring', 'riot', 'ripple'
, 'risk', 'ritual', 'rival', 'river', 'road', 'roast', 'robot', 'robust', 'rocket', 'romance', 'roof'
, 'rookie', 'room', 'rose', 'rotate', 'rough', 'round', 'route', 'royal', 'rubber', 'rude', 'rug', 'rule'
, 'run', 'runway', 'rural', 'sad', 'saddle', 'sadness', 'safe', 'sail', 'salad', 'salmon', 'salon', 'salt'
, 'salute', 'same', 'sample', 'sand', 'satisfy', 'satoshi', 'sauce', 'sausage', 'save', 'say', 'scale'
, 'scan', 'scare', 'scatter', 'scene', 'scheme', 'school', 'science', 'scissors', 'scorpion', 'scout'
, 'scrap', 'screen', 'script', 'scrub', 'sea', 'search', 'season', 'seat', 'second', 'secret', 'section'
, 'security', 'seed', 'seek', 'segment', 'select', 'sell', 'seminar', 'senior', 'sense', 'sentence', 'series'
, 'service', 'session', 'settle', 'setup', 'seven', 'shadow', 'shaft', 'shallow', 'share', 'shed', 'shell'
, 'sheriff', 'shield', 'shift', 'shine', 'ship', 'shiver', 'shock', 'shoe', 'shoot', 'shop', 'short', 'shoulder'
, 'shove', 'shrimp', 'shrug', 'shuffle', 'shy', 'sibling', 'sick', 'side', 'siege', 'sight', 'sign', 'silent'
, 'silk', 'silly', 'silver', 'similar', 'simple', 'since', 'sing', 'siren', 'sister', 'situate', 'six'
, 'size', 'skate', 'sketch', 'ski', 'skill', 'skin', 'skirt', 'skull', 'slab', 'slam', 'sleep', 'slender'
, 'slice', 'slide', 'slight', 'slim', 'slogan', 'slot', 'slow', 'slush', 'small', 'smart', 'smile', 'smoke'
, 'smooth', 'snack', 'snake', 'snap', 'sniff', 'snow', 'soap', 'soccer', 'social', 'sock', 'soda', 'soft'
, 'solar', 'soldier', 'solid', 'solution', 'solve', 'someone', 'song', 'soon', 'sorry', 'sort', 'soul'
, 'sound', 'soup', 'source', 'south', 'space', 'spare', 'spatial', 'spawn', 'speak', 'special', 'speed'
, 'spell', 'spend', 'sphere', 'spice', 'spider', 'spike', 'spin', 'spirit', 'split', 'spoil', 'sponsor'
, 'spoon', 'sport', 'spot', 'spray', 'spread', 'spring', 'spy', 'square', 'squeeze', 'squirrel', 'stable'
, 'stadium', 'staff', 'stage', 'stairs', 'stamp', 'stand', 'start', 'state', 'stay', 'steak', 'steel'
, 'stem', 'step', 'stereo', 'stick', 'still', 'sting', 'stock', 'stomach', 'stone', 'stool', 'story', 'stove'
, 'strategy', 'street', 'strike', 'strong', 'struggle', 'student', 'stuff', 'stumble', 'style', 'subject'
, 'submit', 'subway', 'success', 'such', 'sudden', 'suffer', 'sugar', 'suggest', 'suit', 'summer', 'sun'
, 'sunny', 'sunset', 'super', 'supply', 'supreme', 'sure', 'surface', 'surge', 'surprise', 'surround'
, 'survey', 'suspect', 'sustain', 'swallow', 'swamp', 'swap', 'swarm', 'swear', 'sweet', 'swift', 'swim'
, 'swing', 'switch', 'sword', 'symbol', 'symptom', 'syrup', 'system', 'table', 'tackle', 'tag', 'tail'
, 'talent', 'talk', 'tank', 'tape', 'target', 'task', 'taste', 'tattoo', 'taxi', 'teach', 'team', 'tell'
, 'ten', 'tenant', 'tennis', 'tent', 'term', 'test', 'text', 'thank', 'that', 'theme', 'then', 'theory'
, 'there', 'they', 'thing', 'this', 'thought', 'three', 'thrive', 'throw', 'thumb', 'thunder', 'ticket'
, 'tide', 'tiger', 'tilt', 'timber', 'time', 'tiny', 'tip', 'tired', 'tissue', 'title', 'toast', 'tobacco'
, 'today', 'toddler', 'toe', 'together', 'toilet', 'token', 'tomato', 'tomorrow', 'tone', 'tongue', 'tonight'
, 'tool', 'tooth', 'top', 'topic', 'topple', 'torch', 'tornado', 'tortoise', 'toss', 'total', 'tourist'
, 'toward', 'tower', 'town', 'toy', 'track', 'trade', 'traffic', 'tragic', 'train', 'transfer', 'trap'
, 'trash', 'travel', 'tray', 'treat', 'tree', 'trend', 'trial', 'tribe', 'trick', 'trigger', 'trim', 'trip'
, 'trophy', 'trouble', 'truck', 'true', 'truly', 'trumpet', 'trust', 'truth', 'try', 'tube', 'tuition'
, 'tumble', 'tuna', 'tunnel', 'turkey', 'turn', 'turtle', 'twelve', 'twenty', 'twice', 'twin', 'twist'
, 'two', 'type', 'typical', 'ugly', 'umbrella', 'unable', 'unaware', 'uncle', 'uncover', 'under', 'undo'
, 'unfair', 'unfold', 'unhappy', 'uniform', 'unique', 'unit', 'universe', 'unknown', 'unlock', 'until'
, 'unusual', 'unveil', 'update', 'upgrade', 'uphold', 'upon', 'upper', 'upset', 'urban', 'urge', 'usage'
, 'use', 'used', 'useful', 'useless', 'usual', 'utility', 'vacant', 'vacuum', 'vague', 'valid', 'valley'
, 'valve', 'van', 'vanish', 'vapor', 'various', 'vast', 'vault', 'vehicle', 'velvet', 'vendor', 'venture'
, 'venue', 'verb', 'verify', 'version', 'very', 'vessel', 'veteran', 'viable', 'vibrant', 'vicious', 'victory'
, 'video', 'view', 'village', 'vintage', 'violin', 'virtual', 'virus', 'visa', 'visit', 'visual', 'vital'
, 'vivid', 'vocal', 'voice', 'void', 'volcano', 'volume', 'vote', 'voyage', 'wage', 'wagon', 'wait', 'walk'
, 'wall', 'walnut', 'want', 'warfare', 'warm', 'warrior', 'wash', 'wasp', 'waste', 'water', 'wave', 'way'
, 'wealth', 'weapon', 'wear', 'weasel', 'weather', 'web', 'wedding', 'weekend', 'weird', 'welcome', 'west'
, 'wet', 'whale', 'what', 'wheat', 'wheel', 'when', 'where', 'whip', 'whisper', 'wide', 'width', 'wife'
, 'wild', 'will', 'win', 'window', 'wine', 'wing', 'wink', 'winner', 'winter', 'wire', 'wisdom', 'wise'
, 'wish', 'witness', 'wolf', 'woman', 'wonder', 'wood', 'wool', 'word', 'work', 'world', 'worry', 'worth'
, 'wrap', 'wreck', 'wrestle', 'wrist', 'write', 'wrong', 'yard', 'year', 'yellow', 'you', 'young', 'youth'
, 'zebra', 'zero', 'zone', 'zoo']


BIP39_WORDLIST_MAP = {w: i for i, w in enumerate(BIP39_WORDLIST)}
BIP32_HARDENED = 0x80000000
BIP44_PATH = "m/44'/0'/0'"
WIF_PREFIX = b"\x80"
GBX_ADDRESS_VERSION = 0


class KeyPurpose(Enum):
    EXTERNAL = 0
    INTERNAL = 1
    STAKING = 2
    FUND = 3


def _pbkdf2_hmac_sha512(password: bytes, salt: bytes, iterations: int = 2048) -> bytes:
    return hashlib.pbkdf2_hmac("sha512", password, salt, iterations, dklen=64)


def _hmac_sha512(key: bytes, data: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha512).digest()


def _aes_encrypt(plaintext: bytes, key: bytes) -> Tuple[bytes, bytes, bytes]:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding
    iv = secrets.token_bytes(16)
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac("sha256", key, salt, 100000, dklen=32)
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext) + padder.finalize()
    cipher = Cipher(algorithms.AES(derived), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return ciphertext, iv, salt


def _aes_decrypt(ciphertext: bytes, key: bytes, iv: bytes, salt: bytes) -> bytes:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding
    derived = hashlib.pbkdf2_hmac("sha256", key, salt, 100000, dklen=32)
    cipher = Cipher(algorithms.AES(derived), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(padded) + unpadder.finalize()


def generate_mnemonic(strength: int = 256) -> str:
    if strength not in [128, 160, 192, 224, 256]:
        raise ValueError("Strength must be 128, 160, 192, 224, or 256")
    entropy = secrets.token_bytes(strength // 8)
    ent_bits = int.from_bytes(entropy, "big")
    checksum_size = strength // 32
    checksum = int(hashlib.sha256(entropy).hexdigest(), 16) >> (256 - checksum_size)
    all_bits = (ent_bits << checksum_size) | checksum
    words = []
    total_words = (strength + checksum_size) // 11
    for i in range(total_words):
        idx = (all_bits >> (11 * (total_words - 1 - i))) & 0x7FF
        words.append(BIP39_WORDLIST[idx])
    return " ".join(words)


def mnemonic_to_seed(mnemonic: str, passphrase: str = "") -> bytes:
    return _pbkdf2_hmac_sha512(
        mnemonic.encode("utf-8"),
        ("mnemonic" + passphrase).encode("utf-8"),
        2048
    )


def validate_mnemonic(mnemonic: str) -> bool:
    words = mnemonic.split()
    if len(words) not in [12, 15, 18, 21, 24]:
        return False
    try:
        indices = [BIP39_WORDLIST_MAP[w] for w in words]
    except KeyError:
        return False
    total_bits = len(indices) * 11
    checksum_bits = total_bits // 33
    entropy_bits = total_bits - checksum_bits
    all_bits = 0
    for idx in indices:
        all_bits = (all_bits << 11) | idx
    checksum = all_bits & ((1 << checksum_bits) - 1)
    entropy = all_bits >> checksum_bits
    entropy_bytes = entropy.to_bytes(entropy_bits // 8, "big")
    expected_checksum = int(hashlib.sha256(entropy_bytes).hexdigest(), 16) >> (256 - checksum_bits)
    return checksum == expected_checksum


def entropy_from_mnemonic(mnemonic: str) -> bytes:
    words = mnemonic.split()
    indices = [BIP39_WORDLIST_MAP[w] for w in words]
    total_bits = len(indices) * 11
    checksum_bits = total_bits // 33
    all_bits = 0
    for idx in indices:
        all_bits = (all_bits << 11) | idx
    entropy_bits = total_bits - checksum_bits
    return (all_bits >> checksum_bits).to_bytes(entropy_bits // 8, "big")


class HDNode:
    def __init__(self, private_key: bytes, chain_code: bytes, parent_fingerprint: bytes = b"\x00\x00\x00\x00", depth: int = 0, index: int = 0):
        self.private_key = private_key
        self.chain_code = chain_code
        self.parent_fingerprint = parent_fingerprint
        self.depth = depth
        self.index = index

    @classmethod
    def from_seed(cls, seed: bytes):
        hmac_result = _hmac_sha512(b"Bitcoin seed", seed)
        private_key = hmac_result[:32]
        chain_code = hmac_result[32:]
        return cls(private_key=private_key, chain_code=chain_code)

    @property
    def public_key(self) -> bytes:
        sk = SigningKey.from_string(self.private_key, curve=SECP256k1)
        return sk.verifying_key.to_string("compressed")

    @property
    def identifier(self) -> bytes:
        return utils.hash160(self.public_key)

    @property
    def fingerprint(self) -> bytes:
        return self.identifier[:4]

    def derive_child(self, index: int) -> "HDNode":
        if index >= BIP32_HARDENED:
            data = b"\x00" + self.private_key + struct.pack(">I", index)
        else:
            data = self.public_key + struct.pack(">I", index)
        hmac_result = _hmac_sha512(self.chain_code, data)
        child_private_key = (int.from_bytes(hmac_result[:32], "big") + int.from_bytes(self.private_key, "big")) % SECP256k1.order
        if child_private_key == 0:
            return self.derive_child(index + 1)
        child_private_key_bytes = child_private_key.to_bytes(32, "big")
        child_chain_code = hmac_result[32:]
        return HDNode(
            private_key=child_private_key_bytes,
            chain_code=child_chain_code,
            parent_fingerprint=self.fingerprint,
            depth=self.depth + 1,
            index=index
        )

    def derive_path(self, path: str) -> "HDNode":
        if path == "m":
            return self
        if path.startswith("m/"):
            path = path[2:]
        node = self
        for segment in path.split("/"):
            if segment.endswith("'"):
                idx = int(segment[:-1]) + BIP32_HARDENED
            else:
                idx = int(segment)
            node = node.derive_child(idx)
        return node

    def to_wallet(self) -> "Wallet":
        sk = SigningKey.from_string(self.private_key, curve=SECP256k1)
        return Wallet(signing_key=sk)


class Wallet:
    def __init__(self, signing_key: SigningKey = None, private_key: bytes = None, mnemonic: str = None, wif: str = None, path: str = None):
        if signing_key:
            self.sk = signing_key
        elif private_key:
            self.sk = SigningKey.from_string(private_key, curve=SECP256k1)
        elif mnemonic:
            seed = mnemonic_to_seed(mnemonic)
            hd_node = HDNode.from_seed(seed)
            path = path or BIP44_PATH + "/0'/0/0"
            hd_node = hd_node.derive_path(path)
            self.sk = SigningKey.from_string(hd_node.private_key, curve=SECP256k1)
        elif wif:
            decoded = utils.base58_check_decode(wif)
            if len(decoded) == 33 and decoded[-1:] == b"\x01":
                decoded = decoded[:-1]
            self.sk = SigningKey.from_string(decoded, curve=SECP256k1)
        else:
            self.sk = SigningKey.generate(curve=SECP256k1)
        self.vk = self.sk.verifying_key
        self.public_key = self.vk.to_string("compressed")
        self.address = utils.address_from_public_key(self.public_key)

    @classmethod
    def generate_from_mnemonic(cls, mnemonic: str, path: str = None, passphrase: str = "") -> "Wallet":
        seed = mnemonic_to_seed(mnemonic, passphrase)
        hd_node = HDNode.from_seed(seed)
        path = path or BIP44_PATH + "/0'/0/0"
        hd_node = hd_node.derive_path(path)
        return cls(signing_key=SigningKey.from_string(hd_node.private_key, curve=SECP256k1))

    @classmethod
    def generate_master(cls) -> Tuple["Wallet", str]:
        mnemonic = generate_mnemonic()
        return cls.generate_from_mnemonic(mnemonic), mnemonic

    def sign(self, message: bytes) -> bytes:
        return self.sk.sign(message)

    def verify(self, message: bytes, signature: bytes) -> bool:
        try:
            return self.vk.verify(signature, message)
        except ecdsa.BadSignatureError:
            return False

    def sign_message(self, message: Union[str, bytes]) -> str:
        if isinstance(message, str):
            message = message.encode()
        msg_hash = hashlib.sha256(message).digest()
        sig = self.sk.sign_digest(msg_hash, sigencode=sigencode_der)
        return sig.hex()

    @staticmethod
    def verify_message(address: str, message: Union[str, bytes], signature_hex: str) -> bool:
        if isinstance(message, str):
            message = message.encode()
        try:
            sig = bytes.fromhex(signature_hex)
            r, s = sigdecode_der(sig, SECP256k1.order)
            if r < 1 or r >= SECP256k1.order or s < 1 or s >= SECP256k1.order:
                return False
            msg_hash = hashlib.sha256(message).digest()
            z = int.from_bytes(msg_hash, "big")
            order = SECP256k1.order
            p = SECP256k1.curve.p()
            a = SECP256k1.curve.a()
            b = SECP256k1.curve.b()
            from ecdsa.ellipticcurve import PointJacobi
            curve = SECP256k1.curve
            for recovery_id in range(4):
                try:
                    x = r + (recovery_id // 2) * order
                    if x >= p:
                        continue
                    rhs = (pow(x, 3, p) + a * x + b) % p
                    y = pow(rhs, (p + 1) // 4, p)
                    if (y * y) % p != rhs:
                        continue
                    if recovery_id % 2 != y % 2:
                        y = p - y
                    R = PointJacobi(curve, x, y, 1)
                    inv_r = pow(r, -1, order)
                    u1 = (-z * inv_r) % order
                    u2 = (s * inv_r) % order
                    Q = u1 * SECP256k1.generator + u2 * R
                    vk = VerifyingKey.from_public_point(Q, curve=SECP256k1)
                    recovered_addr = utils.address_from_public_key(vk.to_string("compressed"))
                    if recovered_addr == address:
                        return True
                except Exception:
                    continue
            return False
        except Exception:
            return False

    def get_wif(self) -> str:
        return utils.base58_check_encode(
            self.sk.to_string() + b"\x01",
            version=128
        )

    @classmethod
    def from_wif(cls, wif: str) -> "Wallet":
        decoded = utils.base58_check_decode(wif)
        if decoded[-1:] == b"\x01":
            private_key = decoded[:-1]
        else:
            private_key = decoded
        return cls(private_key=private_key)

    def encrypt(self, passphrase: str) -> dict:
        key = hashlib.sha256(passphrase.encode()).digest()
        plaintext = json.dumps(self.to_dict()).encode()
        ciphertext, iv, salt = _aes_encrypt(plaintext, key)
        return {
            "type": "encrypted",
            "ciphertext": ciphertext.hex(),
            "iv": iv.hex(),
            "salt": salt.hex(),
            "address": self.address,
            "public_key": self.public_key.hex()
        }

    @classmethod
    def decrypt(cls, encrypted: dict, passphrase: str) -> "Wallet":
        key = hashlib.sha256(passphrase.encode()).digest()
        ciphertext = bytes.fromhex(encrypted["ciphertext"])
        iv = bytes.fromhex(encrypted["iv"])
        salt = bytes.fromhex(encrypted["salt"])
        plaintext = _aes_decrypt(ciphertext, key, iv, salt)
        data = json.loads(plaintext.decode())
        return cls(private_key=bytes.fromhex(data["private_key"]))

    def sign_transaction(self, tx: dict) -> dict:
        signed_tx = {k: v for k, v in tx.items() if k not in ("signature", "tx_hash")}
        signed_tx["public_key"] = self.public_key.hex()
        message = json.dumps(signed_tx, sort_keys=True).encode()
        signed_tx["signature"] = self.sign(message).hex()
        return signed_tx

    def to_dict(self) -> dict:
        return {
            "private_key": self.sk.to_string().hex(),
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
        verify_tx = {k: v for k, v in tx.items() if k not in ("signature", "tx_hash")}
        message = json.dumps(verify_tx, sort_keys=True).encode()
        vk = VerifyingKey.from_string(pub_bytes, curve=SECP256k1)
        try:
            return vk.verify(sig_bytes, message)
        except ecdsa.BadSignatureError:
            return False

    @staticmethod
    def create_multisig_address(public_keys: list, required: int) -> Tuple[str, str]:
        if required > len(public_keys):
            raise ValueError("Required signatures cannot exceed number of public keys")
        if required < 1:
            raise ValueError("At least 1 signature required")
        pubkey_bytes = []
        for pk in public_keys:
            if isinstance(pk, str):
                pubkey_bytes.append(bytes.fromhex(pk))
            else:
                pubkey_bytes.append(pk)
        sorted_keys = sorted(pubkey_bytes, key=lambda x: x.hex())
        combined = b"".join([bytes([required + 0x80])] + sorted_keys + [bytes([len(sorted_keys)])])
        address = utils.address_from_public_key(utils.hash160(combined))
        redeem_script = combined.hex()
        return address, redeem_script


class MultiSigWallet:
    def __init__(self, wallets: list, required: int = 2):
        if required > len(wallets):
            raise ValueError("Required signatures exceeds number of wallets")
        self.wallets = wallets
        self.required = required
        public_keys = [w.public_key for w in wallets]
        self.address, self.redeem_script = Wallet.create_multisig_address(public_keys, required)

    def sign_transaction(self, tx: dict) -> dict:
        signed = {k: v for k, v in tx.items() if k not in ("signature", "tx_hash")}
        signatures = []
        for wallet in self.wallets:
            sig_tx = {k: v for k, v in signed.items()}
            sig_tx["public_key"] = wallet.public_key.hex()
            message = json.dumps(sig_tx, sort_keys=True).encode()
            signatures.append(wallet.sign(message).hex())
        signed["multisig"] = True
        signed["signatures"] = signatures
        signed["public_keys"] = [w.public_key.hex() for w in self.wallets]
        signed["required"] = self.required
        signed["redeem_script"] = self.redeem_script
        return signed

    @staticmethod
    def verify_transaction(tx: dict) -> bool:
        if not tx.get("multisig"):
            return Wallet.verify_transaction(tx)
        signatures = tx.get("signatures", [])
        public_keys = tx.get("public_keys", [])
        required = tx.get("required", len(public_keys))
        if len(signatures) < required:
            return False
        base_tx = {k: v for k, v in tx.items() if k not in ("signature", "signatures", "tx_hash", "multisig", "public_keys", "required", "redeem_script")}
        valid_count = 0
        for i, pub_hex in enumerate(public_keys):
            if i >= len(signatures):
                break
            try:
                sig_bytes = bytes.fromhex(signatures[i])
                pub_bytes = bytes.fromhex(pub_hex)
                expected_addr = utils.address_from_public_key(pub_bytes)
                sig_tx = dict(base_tx)
                sig_tx["public_key"] = pub_hex
                message = json.dumps(sig_tx, sort_keys=True).encode()
                vk = VerifyingKey.from_string(pub_bytes, curve=SECP256k1)
                if vk.verify(sig_bytes, message):
                    valid_count += 1
                    if valid_count >= required:
                        return True
            except (ecdsa.BadSignatureError, Exception):
                continue
        return valid_count >= required


class WalletDB:
    def __init__(self, db_path: str = "wallet_data/wallet.db"):
        import sqlite3
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)) or ".", exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS wallets (
                address TEXT PRIMARY KEY,
                label TEXT DEFAULT '',
                encrypted_data TEXT,
                public_key TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                is_hd INTEGER DEFAULT 0,
                mnemonic_hash TEXT DEFAULT '',
                path TEXT DEFAULT '',
                last_used INTEGER DEFAULT 0
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS tx_history (
                tx_hash TEXT PRIMARY KEY,
                address TEXT NOT NULL,
                type TEXT NOT NULL,
                amount INTEGER NOT NULL,
                fee INTEGER DEFAULT 0,
                timestamp INTEGER NOT NULL,
                height INTEGER DEFAULT -1,
                confirmations INTEGER DEFAULT 0,
                counterparty TEXT DEFAULT '',
                memo TEXT DEFAULT '',
                raw_tx TEXT DEFAULT ''
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS address_book (
                address TEXT PRIMARY KEY,
                label TEXT DEFAULT '',
                added_at INTEGER NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS pending_txs (
                tx_hash TEXT PRIMARY KEY,
                raw_tx TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at INTEGER NOT NULL
            )
        """)
        self.conn.commit()

    def save_wallet(self, wallet: Wallet, label: str = "", mnemonic: str = None, path: str = ""):
        c = self.conn.cursor()
        encrypted = None
        mnemonic_hash_val = ""
        if mnemonic:
            mnemonic_hash_val = hashlib.sha256(mnemonic.encode()).hexdigest()
        c.execute("""
            INSERT OR REPLACE INTO wallets
            (address, label, encrypted_data, public_key, created_at, is_hd, mnemonic_hash, path, last_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            wallet.address, label, encrypted, wallet.public_key.hex(),
            int(time.time()), 1 if mnemonic else 0, mnemonic_hash_val,
            path, int(time.time())
        ))
        self.conn.commit()

    def get_wallet(self, address: str) -> Optional[dict]:
        c = self.conn.cursor()
        c.execute("SELECT * FROM wallets WHERE address = ?", (address,))
        row = c.fetchone()
        if not row:
            return None
        return dict(row)

    def list_wallets(self) -> list:
        c = self.conn.cursor()
        c.execute("SELECT w.address, w.label, w.public_key, w.created_at, w.is_hd, w.path, w.last_used, COALESCE(b.balance, 0) as balance FROM wallets w LEFT JOIN (SELECT address, SUM(amount) as balance FROM tx_history GROUP BY address) b ON w.address = b.address ORDER BY w.last_used DESC")
        return [dict(row) for row in c.fetchall()]

    def record_transaction(self, tx_hash: str, address: str, tx_type: str, amount: int, fee: int = 0, timestamp: int = None, height: int = -1, counterparty: str = "", memo: str = "", raw_tx: str = ""):
        c = self.conn.cursor()
        c.execute("""
            INSERT OR IGNORE INTO tx_history
            (tx_hash, address, type, amount, fee, timestamp, height, confirmations, counterparty, memo, raw_tx)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (tx_hash, address, tx_type, amount, fee, timestamp or int(time.time()), height, 0, counterparty, memo, raw_tx))
        self.conn.commit()
        c.execute("UPDATE wallets SET last_used = ? WHERE address = ?", (int(time.time()), address))
        self.conn.commit()

    def get_transaction_history(self, address: str = None, limit: int = 50) -> list:
        c = self.conn.cursor()
        if address:
            c.execute("""
                SELECT * FROM tx_history WHERE address = ?
                ORDER BY timestamp DESC LIMIT ?
            """, (address, limit))
        else:
            c.execute("""
                SELECT * FROM tx_history ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
        return [dict(row) for row in c.fetchall()]

    def add_to_address_book(self, address: str, label: str = ""):
        c = self.conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO address_book (address, label, added_at)
            VALUES (?, ?, ?)
        """, (address, label, int(time.time())))
        self.conn.commit()

    def get_address_book(self) -> list:
        c = self.conn.cursor()
        c.execute("SELECT * FROM address_book ORDER BY added_at DESC")
        return [dict(row) for row in c.fetchall()]

    def save_pending_tx(self, tx_hash: str, raw_tx: dict):
        c = self.conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO pending_txs (tx_hash, raw_tx, status, created_at)
            VALUES (?, ?, 'pending', ?)
        """, (tx_hash, json.dumps(raw_tx), int(time.time())))
        self.conn.commit()

    def confirm_tx(self, tx_hash: str, height: int):
        c = self.conn.cursor()
        c.execute("UPDATE tx_history SET height = ?, confirmations = confirmations + 1 WHERE tx_hash = ?", (height, tx_hash))
        c.execute("UPDATE pending_txs SET status = 'confirmed' WHERE tx_hash = ?", (tx_hash,))
        self.conn.commit()

    def get_pending_txs(self) -> list:
        c = self.conn.cursor()
        c.execute("SELECT * FROM pending_txs WHERE status = 'pending' ORDER BY created_at ASC")
        return [dict(row) for row in c.fetchall()]


class TransactionBuilder:
    @staticmethod
    def create(sender: str, recipient: str, amount: int, fee: int = 0, nonce: int = 0) -> dict:
        return {
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
            "fee": fee,
            "timestamp": time.time(),
            "nonce": nonce,
            "public_key": "",
            "signature": ""
        }

    @staticmethod
    def create_with_change(sender: str, recipient: str, amount: int, fee: int = 0, nonce: int = 0, change_address: str = None) -> dict:
        tx = TransactionBuilder.create(sender, recipient, amount, fee, nonce)
        if change_address:
            tx["change_address"] = change_address
        return tx

    @staticmethod
    def create_staking_tx(sender: str, amount: int, fee: int = 0, nonce: int = 0) -> dict:
        return {
            "sender": sender,
            "recipient": sender,
            "amount": amount,
            "fee": fee,
            "timestamp": time.time(),
            "nonce": nonce,
            "public_key": "",
            "signature": "",
            "tx_type": "stake"
        }

    @staticmethod
    def create_unstake_tx(sender: str, amount: int, fee: int = 0, nonce: int = 0) -> dict:
        return {
            "sender": sender,
            "recipient": sender,
            "amount": amount,
            "fee": fee,
            "timestamp": time.time(),
            "nonce": nonce,
            "public_key": "",
            "signature": "",
            "tx_type": "unstake"
        }

    @staticmethod
    def create_batch(sender: str, outputs: list, fee: int = 0, nonce: int = 0) -> dict:
        total = sum(o["amount"] for o in outputs)
        return {
            "sender": sender,
            "outputs": outputs,
            "total": total,
            "fee": fee,
            "timestamp": time.time(),
            "nonce": nonce,
            "public_key": "",
            "signature": "",
            "tx_type": "batch"
        }

    @staticmethod
    def estimate_fee(tx: dict, fee_per_byte: int = 1) -> int:
        raw = json.dumps(tx, sort_keys=True)
        return max(len(raw.encode()) * fee_per_byte, config.DUST_LIMIT)


def create_transaction(sender: str, recipient: str, amount: int, fee: int = 0, nonce: int = 0) -> dict:
    return TransactionBuilder.create(sender, recipient, amount, fee, nonce)
