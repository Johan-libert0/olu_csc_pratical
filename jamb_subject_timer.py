"""
JAMB CBT Practice — All Subjects, Subject-Level Timer
=======================================================
- All subjects shown as a flat grid (no category grouping)
- Calculation subjects (Maths, Physics, Further Maths, Chemistry, Accounting): 10 min total per subject
- All other subjects: 7 min total per subject
- Timer counts down from start of first question; covers all 10 questions
- Green/red answer highlighting, score tracking, summary screen

Run:
    pip install streamlit
    streamlit run jamb_subject_timer.py
"""

import streamlit as st
import time

st.set_page_config(page_title="JAMB CBT Practice", page_icon="🎓", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* ── Landing ── */
.hero { text-align:center; padding: 3rem 1rem 1.5rem; }
.hero-title {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2rem, 6vw, 3.4rem);
  font-weight: 700; line-height: 1.15; margin-bottom: .6rem;
}
.hero-sub {
  color: #6B7A90; font-size: 1.05rem;
  line-height: 1.75; max-width: 540px; margin: 0 auto 1.75rem;
}
.chip-row { display:flex; flex-wrap:wrap; gap:8px; justify-content:center; margin-bottom:2rem; }
.chip { background:#F3F6FA; border-radius:999px; padding:5px 14px; font-size:13px; color:#4A5568; border:1px solid #E2E8F0; }
.stat-row { display:flex; justify-content:center; gap:3rem; margin-top:2rem; flex-wrap:wrap; }
.stat { text-align:center; }
.stat-num { font-size:2rem; font-weight:700; }
.stat-lbl { font-size:11px; color:#9AA5B4; letter-spacing:.05em; text-transform:uppercase; margin-top:2px; }

/* ── Subject cards ── */
.subj-card {
  border-radius:14px; padding:1.1rem 1.2rem;
  border:1px solid #E5EAF2; background:#FAFBFC;
  transition: box-shadow .15s, transform .15s;
  margin-bottom: 4px;
}
.subj-card:hover { box-shadow:0 6px 20px rgba(0,0,0,.09); transform:translateY(-2px); }
.subj-icon { font-size:1.5rem; margin-bottom:.35rem; }
.subj-name { font-size:.88rem; font-weight:500; margin-bottom:.15rem; }
.subj-desc { font-size:10.5px; color:#9AA5B4; margin-bottom:.3rem; }
.subj-timer { font-size:11px; color:#718096; }
.subj-score { font-size:11px; font-weight:500; margin-top:4px; }

/* ── Timer ── */
.timer-bar-wrap {
  width: 100%; height: 10px;
  background: #EDF2F7; border-radius: 999px;
  margin-bottom: 1.25rem; overflow: hidden;
}
.timer-bar { height: 100%; border-radius: 999px; transition: width .9s linear, background .5s; }

.timer-label {
  display: flex; justify-content: space-between;
  align-items: center; font-size: 13px; margin-bottom: .4rem;
}
.timer-text-normal { color: #2B6CB0; font-weight: 500; }
.timer-text-warn   { color: #C05621; font-weight: 500; }
.timer-text-danger { color: #C53030; font-weight: 600; animation: blink .6s infinite alternate; }
@keyframes blink { from{opacity:1} to{opacity:.5} }

/* ── Options ── */
.opt-correct { background:#E1F5EE!important; border:1.5px solid #1D9E75!important; color:#085041!important; border-radius:10px; padding:12px 16px; margin:5px 0; font-size:15px; }
.opt-wrong   { background:#FCEBEB!important; border:1.5px solid #E24B4A!important; color:#501313!important; border-radius:10px; padding:12px 16px; margin:5px 0; font-size:15px; }
.opt-reveal  { background:#E8F5E9!important; border:1.5px dashed #1D9E75!important; color:#1B5E20!important; border-radius:10px; padding:12px 16px; margin:5px 0; font-size:15px; opacity:.85; }
.opt-neutral { background:#F8F9FA!important; border:1px solid #E2E8F0!important; color:#2D3748!important; border-radius:10px; padding:12px 16px; margin:5px 0; font-size:15px; }
.opt-timeout { background:#F0F4F8!important; border:1px solid #CBD5E0!important; color:#A0AEC0!important; border-radius:10px; padding:12px 16px; margin:5px 0; font-size:15px; }

.timeout-badge {
  background:#FFF5F5; border:1.5px solid #FC8181; color:#C53030;
  border-radius:10px; padding:10px 16px; font-size:14px;
  font-weight:500; margin-bottom:.75rem; text-align:center;
}
.calc-badge {
  display:inline-block; background:#FFF3CD; color:#856404;
  font-size:11px; padding:2px 9px; border-radius:999px;
  font-weight:500; margin-left:8px; vertical-align:middle;
}

/* ── Summary ── */
.sum-card { background:#F7F9FC; border-radius:12px; padding:1rem; text-align:center; border:1px solid #E5E9F0; }
.sum-num { font-size:1.9rem; font-weight:600; }
.sum-lbl { font-size:12px; color:#9AA5B4; margin-top:3px; }
</style>
""", unsafe_allow_html=True)

# ── Subject definitions ────────────────────────────────────────────────────────
# calc_subject=True  → 10-minute subject timer
# calc_subject=False → 7-minute subject timer

SUBJECTS = [
    {
        "id": "biology", "label": "Biology", "icon": "🧬", "color": "#1D9E75",
        "desc": "Cell biology, genetics, ecology", "calc_subject": False,
        "questions": [
            {"q": "What is the powerhouse of the cell?", "opts": ["Nucleus","Mitochondria","Ribosome","Golgi apparatus"], "a": 1},
            {"q": "Which molecule carries genetic information?", "opts": ["RNA","ATP","DNA","Protein"], "a": 2},
            {"q": "What process converts sunlight to energy in plants?", "opts": ["Respiration","Fermentation","Photosynthesis","Osmosis"], "a": 2},
            {"q": "How many chromosomes do human body cells contain?", "opts": ["23","44","46","48"], "a": 2},
            {"q": "Which blood type is the universal donor?", "opts": ["AB+","O−","A+","B−"], "a": 1},
            {"q": "What is the basic structural unit of life?", "opts": ["Tissue","Organ","Cell","Atom"], "a": 2},
            {"q": "Which brain region controls balance and coordination?", "opts": ["Cerebrum","Medulla","Hypothalamus","Cerebellum"], "a": 3},
            {"q": "What bond holds the DNA double helix together?", "opts": ["Ionic","Covalent","Hydrogen","Peptide"], "a": 2},
            {"q": "Which organelle handles protein synthesis?", "opts": ["Lysosome","Ribosome","Vacuole","Centrosome"], "a": 1},
            {"q": "Organisms that make their own food are called?", "opts": ["Heterotrophs","Decomposers","Autotrophs","Parasites"], "a": 2},
        ],
    },
    {
        "id": "chemistry", "label": "Chemistry", "icon": "⚗️", "color": "#378ADD",
        "desc": "Periodic table, bonding, reactions", "calc_subject": True,
        "questions": [
            {"q": "What is the chemical symbol for gold?", "opts": ["Gd","Go","Au","Ag"], "a": 2},
            {"q": "How many elements are in the periodic table?", "opts": ["108","112","118","124"], "a": 2},
            {"q": "What is the pH of a neutral solution at 25°C?", "opts": ["5","6","7","8"], "a": 2},
            {"q": "Which gas makes up most of Earth's atmosphere?", "opts": ["Oxygen","Carbon dioxide","Nitrogen","Argon"], "a": 2},
            {"q": "What is the chemical formula for water?", "opts": ["HO","H2O","H2O2","HO2"], "a": 1},
            {"q": "Which subatomic particle carries a negative charge?", "opts": ["Proton","Neutron","Electron","Quark"], "a": 2},
            {"q": "What bond involves sharing of electrons?", "opts": ["Ionic","Covalent","Metallic","Hydrogen"], "a": 1},
            {"q": "What is the molar mass of NaCl (g/mol)?", "opts": ["23","35.5","58.5","74"], "a": 2},
            {"q": "How many moles are in 44g of CO₂ (molar mass=44)?", "opts": ["0.5","1","2","4"], "a": 1},
            {"q": "Which acid is found in the human stomach?", "opts": ["Sulfuric","Nitric","Hydrochloric","Acetic"], "a": 2},
        ],
    },
    {
        "id": "physics", "label": "Physics", "icon": "⚡", "color": "#7B4FBF",
        "desc": "Mechanics, waves, electricity, optics", "calc_subject": True,
        "questions": [
            {"q": "What is the SI unit of force?", "opts": ["Watt","Joule","Newton","Pascal"], "a": 2},
            {"q": "What is the speed of light in a vacuum?", "opts": ["3×10⁶ m/s","3×10⁸ m/s","3×10¹⁰ m/s","3×10⁴ m/s"], "a": 1},
            {"q": "Which law states every action has an equal and opposite reaction?", "opts": ["Newton's 1st","Newton's 2nd","Newton's 3rd","Hooke's Law"], "a": 2},
            {"q": "What type of wave is sound?", "opts": ["Transverse","Electromagnetic","Longitudinal","Surface"], "a": 2},
            {"q": "What is the unit of electrical resistance?", "opts": ["Ampere","Volt","Ohm","Watt"], "a": 2},
            {"q": "A body of mass 5kg moves at 10m/s. What is its kinetic energy?", "opts": ["50 J","250 J","500 J","25 J"], "a": 1},
            {"q": "What is the formula for kinetic energy?", "opts": ["mgh","½mv²","mv","Fd"], "a": 1},
            {"q": "A 60W bulb runs for 2 hours. Energy used in kWh?", "opts": ["0.06 kWh","0.12 kWh","1.2 kWh","12 kWh"], "a": 1},
            {"q": "What phenomenon explains bending of light at an interface?", "opts": ["Reflection","Diffraction","Refraction","Interference"], "a": 2},
            {"q": "Using V=IR, if V=12V and R=4Ω, what is I?", "opts": ["3A","4A","6A","48A"], "a": 0},
        ],
    },
    {
        "id": "mathematics", "label": "Mathematics", "icon": "📐", "color": "#D4537E",
        "desc": "Algebra, geometry, statistics", "calc_subject": True,
        "questions": [
            {"q": "What is the value of π to two decimal places?", "opts": ["3.12","3.14","3.16","3.18"], "a": 1},
            {"q": "What is the square root of 144?", "opts": ["10","11","12","13"], "a": 2},
            {"q": "Solve: 2x + 5 = 13. What is x?", "opts": ["3","4","5","6"], "a": 1},
            {"q": "What is 15% of 200?", "opts": ["20","25","30","35"], "a": 2},
            {"q": "Sum of interior angles of a triangle?", "opts": ["90°","120°","180°","360°"], "a": 2},
            {"q": "What is 7! (7 factorial)?", "opts": ["2520","5040","720","40320"], "a": 1},
            {"q": "Area of a circle with radius 5 (π≈3.14)?", "opts": ["31.4","62.8","78.5","15.7"], "a": 2},
            {"q": "Which is a prime number?", "opts": ["15","21","29","33"], "a": 2},
            {"q": "What is log₁₀(1000)?", "opts": ["2","3","4","5"], "a": 1},
            {"q": "If 3x − 7 = 2x + 5, find x.", "opts": ["10","11","12","13"], "a": 2},
        ],
    },
    {
        "id": "further_maths", "label": "Further Maths", "icon": "🔢", "color": "#C0392B",
        "desc": "Calculus, matrices, complex numbers", "calc_subject": True,
        "questions": [
            {"q": "What is the derivative of x²?", "opts": ["x","2x","2x²","x³"], "a": 1},
            {"q": "What is the integral of 2x dx?", "opts": ["x²+C","2x²+C","x+C","2+C"], "a": 0},
            {"q": "Modulus of complex number 3+4i?", "opts": ["3","4","5","7"], "a": 2},
            {"q": "Determinant of [[2,3],[1,4]]?", "opts": ["5","8","11","−5"], "a": 0},
            {"q": "Sum of infinite geometric series a=1, r=½?", "opts": ["1","1.5","2","3"], "a": 2},
            {"q": "sin²θ + cos²θ equals?", "opts": ["0","2","1","sinθcosθ"], "a": 2},
            {"q": "Gradient of a curve at a point is found using?", "opts": ["Integration","Differentiation","Factorisation","Substitution"], "a": 1},
            {"q": "Value of ⁵C₂?", "opts": ["5","10","15","20"], "a": 1},
            {"q": "log(ab) equals?", "opts": ["log a × log b","log a + log b","log a − log b","log(a/b)"], "a": 1},
            {"q": "If f(x)=3x²−2x, find f'(x)?", "opts": ["6x","6x−2","3x−2","6x+2"], "a": 1},
        ],
    },
    {
        "id": "computer_science", "label": "Computer Science", "icon": "💻", "color": "#0EA5C9",
        "desc": "Hardware, software, programming", "calc_subject": False,
        "questions": [
            {"q": "What does CPU stand for?", "opts": ["Central Processing Unit","Computer Personal Unit","Central Program Utility","Core Processing Unit"], "a": 0},
            {"q": "Which is an input device?", "opts": ["Monitor","Printer","Keyboard","Speaker"], "a": 2},
            {"q": "What does RAM stand for?", "opts": ["Read Access Memory","Random Access Memory","Rapid Application Memory","Read Application Memory"], "a": 1},
            {"q": "Which number system uses only 0 and 1?", "opts": ["Octal","Hexadecimal","Binary","Decimal"], "a": 2},
            {"q": "Convert binary 1010 to decimal.", "opts": ["8","10","12","14"], "a": 1},
            {"q": "What does HTML stand for?", "opts": ["Hyper Text Markup Language","High Text Making Language","Hyper Transfer Markup Link","Home Tool Markup Language"], "a": 0},
            {"q": "Which is NOT a programming language?", "opts": ["Python","Java","Linux","C++"], "a": 2},
            {"q": "What is a byte made up of?", "opts": ["4 bits","16 bits","8 bits","2 bits"], "a": 2},
            {"q": "Which device connects computers in a network?", "opts": ["Monitor","Router","Scanner","Projector"], "a": 1},
            {"q": "Convert hexadecimal F to decimal.", "opts": ["14","15","16","17"], "a": 1},
        ],
    },
    {
        "id": "agriculture", "label": "Agriculture", "icon": "🌾", "color": "#5D8A3C",
        "desc": "Crop science, animal husbandry, soil", "calc_subject": False,
        "questions": [
            {"q": "Which soil type is best for crop production?", "opts": ["Sandy","Clay","Loamy","Silty"], "a": 2},
            {"q": "What does N in NPK fertiliser stand for?", "opts": ["Nitrogen","Sodium","Nickel","Neon"], "a": 0},
            {"q": "Which is a leguminous crop?", "opts": ["Maize","Cassava","Groundnut","Yam"], "a": 2},
            {"q": "Raising fish in controlled environments is called?", "opts": ["Apiculture","Pisciculture","Silviculture","Horticulture"], "a": 1},
            {"q": "What does pH measure in soil?", "opts": ["Moisture","Acidity or alkalinity","Temperature","Nitrogen content"], "a": 1},
            {"q": "Primary purpose of crop rotation?", "opts": ["Increase rainfall","Maintain soil fertility","Kill pests","Reduce weeds"], "a": 1},
            {"q": "A field is 200m × 50m. Area in hectares? (1ha=10,000m²)", "opts": ["0.5 ha","1 ha","2 ha","10 ha"], "a": 1},
            {"q": "Which is a cash crop in Nigeria?", "opts": ["Cassava","Cocoa","Yam","Plantain"], "a": 1},
            {"q": "Gestation period of a cow (approx)?", "opts": ["3 months","6 months","9 months","12 months"], "a": 2},
            {"q": "What is apiculture?", "opts": ["Fish farming","Bee keeping","Snail farming","Silk worm rearing"], "a": 1},
        ],
    },
    {
        "id": "english", "label": "English Language", "icon": "📖", "color": "#BA7517",
        "desc": "Grammar, comprehension, literature", "calc_subject": False,
        "questions": [
            {"q": "What is the plural of 'criterion'?", "opts": ["Criterions","Criteria","Criterias","Criterium"], "a": 1},
            {"q": "Which sentence is grammatically correct?", "opts": ["She don't know","She doesn't know","She not know","She knowsn't"], "a": 1},
            {"q": "'The wind whispered' — which literary device?", "opts": ["Simile","Metaphor","Personification","Hyperbole"], "a": 2},
            {"q": "Synonym of 'benevolent'?", "opts": ["Cruel","Kind","Shy","Loud"], "a": 1},
            {"q": "Antonym of 'verbose'?", "opts": ["Wordy","Lengthy","Concise","Elaborate"], "a": 2},
            {"q": "Who wrote 'Romeo and Juliet'?", "opts": ["Dickens","Austen","Shakespeare","Chaucer"], "a": 2},
            {"q": "What punctuation ends an exclamatory sentence?", "opts": ["Period","Comma","Question mark","Exclamation mark"], "a": 3},
            {"q": "'It's raining cats and dogs' is an example of?", "opts": ["Metaphor","Simile","Idiom","Alliteration"], "a": 2},
            {"q": "Past tense of 'swim'?", "opts": ["Swimmed","Swam","Swum","Swimed"], "a": 1},
            {"q": "A word that modifies a noun is called a?", "opts": ["Verb","Adverb","Adjective","Pronoun"], "a": 2},
        ],
    },
    {
        "id": "literature", "label": "Literature", "icon": "📜", "color": "#8E44AD",
        "desc": "Poetry, prose, drama, African lit", "calc_subject": False,
        "questions": [
            {"q": "Who wrote 'Things Fall Apart'?", "opts": ["Wole Soyinka","Chinua Achebe","Ngugi wa Thiong'o","Ben Okri"], "a": 1},
            {"q": "What is a soliloquy?", "opts": ["Dialogue between two","Character speaking thoughts aloud alone","14-line poem","Type of metaphor"], "a": 1},
            {"q": "Which is a tragedy by Shakespeare?", "opts": ["A Midsummer Night's Dream","Hamlet","The Tempest","Twelfth Night"], "a": 1},
            {"q": "The main character of a story is called?", "opts": ["Antagonist","Narrator","Protagonist","Foil"], "a": 2},
            {"q": "Rhyme scheme of a Shakespearean sonnet?", "opts": ["ABAB CDCD EFEF GG","ABBA CDDC EE","AABB CCDD","ABCD ABCD"], "a": 0},
            {"q": "Who wrote 'Death and the King's Horseman'?", "opts": ["Chinua Achebe","Cyprian Ekwensi","Wole Soyinka","J.P. Clark"], "a": 2},
            {"q": "A story using animals to teach a moral is called?", "opts": ["A myth","A fable","An epic","A ballad"], "a": 1},
            {"q": "The turning point in a play is called?", "opts": ["Exposition","Climax","Resolution","Prologue"], "a": 1},
            {"q": "Which device uses 'like' or 'as' to compare?", "opts": ["Metaphor","Simile","Alliteration","Irony"], "a": 1},
            {"q": "What is a haiku?", "opts": ["14-line poem","3-line Japanese poem","Epic poem","Rhyming couplet"], "a": 1},
        ],
    },
    {
        "id": "government", "label": "Government", "icon": "🏛️", "color": "#2471A3",
        "desc": "Political systems, democracy, Nigeria", "calc_subject": False,
        "questions": [
            {"q": "What type of government does Nigeria practise?", "opts": ["Monarchy","Theocracy","Federal Republic","Confederacy"], "a": 2},
            {"q": "How many tiers of government are in Nigeria?", "opts": ["2","3","4","5"], "a": 1},
            {"q": "The highest law in Nigeria is?", "opts": ["Criminal Code","Penal Code","The Constitution","Electoral Act"], "a": 2},
            {"q": "Nigeria's legislature is called?", "opts": ["The Cabinet","Supreme Court","National Assembly","Senate only"], "a": 2},
            {"q": "Separation of powers means?", "opts": ["One person holds all power","Power divided among three arms","States have more power","Military controls government"], "a": 1},
            {"q": "Head of state in a presidential system?", "opts": ["Prime Minister","President","Chancellor","Governor"], "a": 1},
            {"q": "What is a referendum?", "opts": ["Election for parliament","Direct vote by the public on an issue","Military coup","A type of bill"], "a": 1},
            {"q": "INEC stands for?", "opts": ["Independent National Electoral Commission","Internal National Election Committee","Integrated National Electoral Council","Independent National Election Council"], "a": 0},
            {"q": "Principle of checks and balances means?", "opts": ["Each arm monitors the others","Citizens check military","States check federal","Courts check citizens"], "a": 0},
            {"q": "Which body interprets the Nigerian constitution?", "opts": ["National Assembly","The President","The Supreme Court","INEC"], "a": 2},
        ],
    },
    {
        "id": "crs", "label": "CRS / MRS", "icon": "✝️", "color": "#6C3483",
        "desc": "Christian and Muslim Religious Studies", "calc_subject": False,
        "questions": [
            {"q": "Who was the first man according to the Bible?", "opts": ["Noah","Abraham","Adam","Moses"], "a": 2},
            {"q": "How many books are in the Old Testament?", "opts": ["27","39","66","46"], "a": 1},
            {"q": "Who led the Israelites out of Egypt?", "opts": ["Abraham","David","Solomon","Moses"], "a": 3},
            {"q": "First book of the Bible?", "opts": ["Exodus","Psalms","Genesis","Matthew"], "a": 2},
            {"q": "How many pillars of faith are in Islam?", "opts": ["3","4","5","6"], "a": 2},
            {"q": "The holy book of Islam is?", "opts": ["Bible","Torah","Quran","Vedas"], "a": 2},
            {"q": "Last prophet in Islam?", "opts": ["Isa","Musa","Ibrahim","Muhammad"], "a": 3},
            {"q": "First surah of the Quran?", "opts": ["Al-Baqarah","Al-Fatiha","An-Nas","Al-Ikhlas"], "a": 1},
            {"q": "Christian doctrine of the Trinity refers to?", "opts": ["Three gods","Father, Son, Holy Spirit","Three prophets","Three angels"], "a": 1},
            {"q": "Ramadan is the month of fasting in?", "opts": ["Christianity","Judaism","Islam","Hinduism"], "a": 2},
        ],
    },
    {
        "id": "economics", "label": "Economics", "icon": "📈", "color": "#16A085",
        "desc": "Micro, macro, demand, supply, trade", "calc_subject": False,
        "questions": [
            {"q": "What does GDP stand for?", "opts": ["Gross Domestic Product","General Domestic Price","Gross Demand Product","General Demand Price"], "a": 0},
            {"q": "Law of demand: as price rises, quantity demanded?", "opts": ["Increases","Stays same","Decreases","Doubles"], "a": 2},
            {"q": "What is inflation?", "opts": ["Fall in prices","Rise in general price levels","Decrease in money supply","Increase in exports"], "a": 1},
            {"q": "Which is a factor of production?", "opts": ["Money","Land","Profit","Tax"], "a": 1},
            {"q": "A market with one seller is called?", "opts": ["Oligopoly","Perfect competition","Monopoly","Duopoly"], "a": 2},
            {"q": "Total revenue ₦50,000, total cost ₦32,000. Profit is?", "opts": ["₦18,000","₦82,000","₦32,000","₦50,000"], "a": 0},
            {"q": "When supply exceeds demand, price tends to?", "opts": ["Rise","Fall","Stay same","Double"], "a": 1},
            {"q": "Opportunity cost means?", "opts": ["Cost of production","Next best alternative forgone","Total cost of goods","Price of imports"], "a": 1},
            {"q": "Which institution controls money supply in Nigeria?", "opts": ["FIRS","CBN","SEC","NDIC"], "a": 1},
            {"q": "Budget deficit means?", "opts": ["Revenue > expenditure","Expenditure > revenue","Revenue = expenditure","No spending"], "a": 1},
        ],
    },
    {
        "id": "accounting", "label": "Accounting", "icon": "🧾", "color": "#E67E22",
        "desc": "Financial statements, bookkeeping", "calc_subject": True,
        "questions": [
            {"q": "The accounting equation is?", "opts": ["Assets = Liabilities + Capital","Assets = Revenue − Expenses","Capital = Assets + Liabilities","Revenue = Assets − Liabilities"], "a": 0},
            {"q": "A balance sheet shows?", "opts": ["Daily sales","Assets, liabilities, and capital","Cash flow only","Profit and loss"], "a": 1},
            {"q": "Money owed to a business is recorded in?", "opts": ["Creditors","Debtors","Capital account","Expenses account"], "a": 1},
            {"q": "Debit means in double-entry?", "opts": ["Money leaving","Entry on the left","Entry on the right","Revenue received"], "a": 1},
            {"q": "Depreciation is?", "opts": ["Increase in asset value","Reduction in asset value over time","Profit from selling asset","Cash paid for asset"], "a": 1},
            {"q": "Assets=₦80,000, Liabilities=₦35,000. Capital is?", "opts": ["₦115,000","₦45,000","₦35,000","₦80,000"], "a": 1},
            {"q": "A trial balance checks that?", "opts": ["Debits equal credits","Assets equal liabilities","Revenue equals expenses","Cash equals capital"], "a": 0},
            {"q": "Current assets=₦60k, Current liabilities=₦25k. Working capital?", "opts": ["₦85,000","₦35,000","₦25,000","₦60,000"], "a": 1},
            {"q": "Example of a fixed asset?", "opts": ["Cash","Debtors","Stock","Land and buildings"], "a": 3},
            {"q": "FIFO stands for?", "opts": ["First In First Out","Final Invoice For Orders","Fixed Income For Operations","First Invoice Final Output"], "a": 0},
        ],
    },
    {
        "id": "commerce", "label": "Commerce", "icon": "🏪", "color": "#27AE60",
        "desc": "Trade, banking, insurance, transport", "calc_subject": False,
        "questions": [
            {"q": "Commerce covers?", "opts": ["Production of goods only","All activities aiding buying and selling","Manufacturing only","Agricultural trade"], "a": 1},
            {"q": "A wholesaler?", "opts": ["Sells to final consumer","Buys bulk and sells to retailers","Manufacturer's agent","Transport company"], "a": 1},
            {"q": "Insurance provides?", "opts": ["Loans to businesses","Protection against financial loss","Investment returns","Tax benefits"], "a": 1},
            {"q": "A bill of lading is used in?", "opts": ["Banking","Insurance","Shipping","Retailing"], "a": 2},
            {"q": "E-commerce is?", "opts": ["A physical market","Online platform for buying and selling","A stock exchange","A government trade body"], "a": 1},
            {"q": "Primary function of a central bank?", "opts": ["Give loans to individuals","Regulate money supply and banking","Sell government bonds only","Collect taxes"], "a": 1},
            {"q": "A cheque is?", "opts": ["A currency note","A written order to a bank to pay a sum","A receipt","A bank statement"], "a": 1},
            {"q": "Goods bought from other countries are called?", "opts": ["Exports","Imports","Tariffs","Quotas"], "a": 1},
            {"q": "A cooperative society is?", "opts": ["A government company","People pooling resources for mutual benefit","A private limited company","A foreign-owned business"], "a": 1},
            {"q": "Articles of Association state?", "opts": ["Balance sheet","Internal rules of a company","Memorandum of Association","Prospectus"], "a": 1},
        ],
    },
    {
        "id": "geography", "label": "Geography", "icon": "🌍", "color": "#2980B9",
        "desc": "Physical and human geography, maps", "calc_subject": False,
        "questions": [
            {"q": "Largest continent by area?", "opts": ["Africa","North America","Asia","Europe"], "a": 2},
            {"q": "Capital of Nigeria?", "opts": ["Lagos","Kano","Abuja","Ibadan"], "a": 2},
            {"q": "Longest river in Africa?", "opts": ["Congo","Niger","Nile","Zambezi"], "a": 2},
            {"q": "Rock formed from cooled magma?", "opts": ["Sedimentary","Metamorphic","Igneous","Limestone"], "a": 2},
            {"q": "Imaginary line at 0° longitude?", "opts": ["Equator","Tropic of Cancer","Prime Meridian","International Date Line"], "a": 2},
            {"q": "Nigeria is mostly in which climate zone?", "opts": ["Temperate","Polar","Tropical","Desert"], "a": 2},
            {"q": "Urbanisation is?", "opts": ["Movement from cities to rural","Growth of cities due to rural-urban migration","Building roads in rural areas","Increase in agricultural output"], "a": 1},
            {"q": "Contour lines on a map represent?", "opts": ["Rivers","Roads","Points of equal elevation","Political boundaries"], "a": 2},
            {"q": "The greenhouse effect is?", "opts": ["Cooling of earth","Trapping of heat in atmosphere","Growing plants in glass houses","Reduction of rainfall"], "a": 1},
            {"q": "The Ring of Fire is?", "opts": ["Desert belt around Sahara","Zone of high volcanic activity around the Pacific","Tropical rainforest belt","Zone of high rainfall"], "a": 1},
        ],
    },
]

LABELS       = "ABCD"
NORMAL_TIME  = 7 * 60    # 7 minutes in seconds
CALC_TIME    = 10 * 60   # 10 minutes in seconds

# ── Session state init ─────────────────────────────────────────────────────────
def init():
    st.session_state.setdefault("screen", "landing")
    st.session_state.setdefault("active_subject", None)
    st.session_state.setdefault("q_idx", 0)
    st.session_state.setdefault("score", 0)
    st.session_state.setdefault("selected", None)
    st.session_state.setdefault("locked", False)
    st.session_state.setdefault("timed_out", False)
    st.session_state.setdefault("subject_timer_start", None)
    st.session_state.setdefault("subject_scores", {})

init()

def go(screen, **kwargs):
    st.session_state.screen = screen
    for k, v in kwargs.items():
        st.session_state[k] = v

def get_subject(sid):
    return next((s for s in SUBJECTS if s["id"] == sid), None)

def get_grade(pct):
    if pct == 100: return "🏆 Perfect score! Outstanding — full marks!"
    if pct >= 80:  return "🎉 Excellent — you are well prepared for JAMB!"
    if pct >= 60:  return "👍 Good effort — keep reviewing and you'll ace it."
    if pct >= 40:  return "📚 Fair attempt — more practice will boost your score."
    return "💪 Keep at it — consistent practice makes perfect."

def fmt_time(secs):
    m, s = divmod(max(0, secs), 60)
    return f"{m:02d}:{s:02d}"

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 1 — Landing
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.screen == "landing":
    total_q = sum(len(s["questions"]) for s in SUBJECTS)
    calc_subjects = [s["label"] for s in SUBJECTS if s["calc_subject"]]

    st.markdown(f"""
    <div class="hero">
      <div class="hero-title">🎓 JAMB CBT Practice</div>
      <div class="hero-sub">
        Sharpen your UTME score with timed, subject-based mock tests covering
        all Science, Arts &amp; Commercial subjects. Each subject is timed —
        calculation subjects get <strong>10 minutes</strong>, all others get <strong>7 minutes</strong>.
      </div>
      <div class="chip-row">
        <span class="chip">🧬 Science</span>
        <span class="chip">📚 Arts</span>
        <span class="chip">💰 Commercial</span>
        <span class="chip">⏱️ Subject Timer</span>
        <span class="chip">✅ Instant Feedback</span>
        <span class="chip">🇳🇬 UTME Focused</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Start Practice →", use_container_width=True, type="primary"):
            go("subjects")
            st.rerun()

    st.markdown(f"""
    <div class="stat-row">
      <div class="stat"><div class="stat-num">{total_q}</div><div class="stat-lbl">Total Questions</div></div>
      <div class="stat"><div class="stat-num">{len(SUBJECTS)}</div><div class="stat-lbl">Subjects</div></div>
      <div class="stat"><div class="stat-num">7 / 10</div><div class="stat-lbl">Mins Per Subject</div></div>
      <div class="stat"><div class="stat-num">100%</div><div class="stat-lbl">Free to Use</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown(f"**📊 Calculation subjects (10 min):** {', '.join(calc_subjects)}")

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 2 — Subject Selection (flat grid)
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "subjects":
    if st.button("← Back to Home"):
        go("landing"); st.rerun()

    st.markdown("## Choose a Subject")
    st.caption("Calculation subjects (📊) get 10 minutes · All others get 7 minutes")
    st.markdown("")

    cols = st.columns(3)
    for i, sub in enumerate(SUBJECTS):
        sid       = sub["id"]
        sc        = st.session_state.subject_scores.get(sid)
        pct       = round(sc / 10 * 100) if sc is not None else None
        timer_lbl = "⏱️ 10 min" if sub["calc_subject"] else "⏱️ 7 min"
        score_html = (
            f'<div class="subj-score" style="color:{sub["color"]}">Last: {sc}/10 ({pct}%)</div>'
            if sc is not None else
            '<div class="subj-score" style="color:#CCC">Not attempted</div>'
        )
        calc_icon = " 📊" if sub["calc_subject"] else ""
        with cols[i % 3]:
            st.markdown(f"""
            <div class="subj-card">
              <div class="subj-icon">{sub['icon']}</div>
              <div class="subj-name" style="color:{sub['color']}">{sub['label']}{calc_icon}</div>
              <div class="subj-desc">{sub['desc']}</div>
              <div class="subj-timer">{timer_lbl}</div>
              {score_html}
            </div>
            """, unsafe_allow_html=True)
            if st.button("Start" if sc is None else "Retry", key=f"btn_{sid}", use_container_width=True):
                go("quiz", active_subject=sid, q_idx=0, score=0,
                   selected=None, locked=False, timed_out=False,
                   subject_timer_start=time.time())
                st.rerun()

    if st.session_state.subject_scores:
        st.markdown("---")
        if st.button("📊 View Overall Results", use_container_width=True):
            go("overall"); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 3 — Quiz (subject-level timer)
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "quiz":
    sub        = get_subject(st.session_state.active_subject)
    q_idx      = st.session_state.q_idx
    total_qs   = len(sub["questions"])
    q          = sub["questions"][q_idx]
    time_limit = CALC_TIME if sub["calc_subject"] else NORMAL_TIME

    # ── Subject timer ──────────────────────────────────────────────────────────
    if st.session_state.subject_timer_start is None:
        st.session_state.subject_timer_start = time.time()

    elapsed   = int(time.time() - st.session_state.subject_timer_start)
    remaining = max(0, time_limit - elapsed)
    pct_left  = remaining / time_limit

    # Auto-timeout: skip remaining questions when time runs out
    if remaining == 0 and not st.session_state.timed_out:
        # Mark all unanswered questions as timed-out, lock current question
        st.session_state.locked    = True
        st.session_state.timed_out = True
        if st.session_state.selected is None:
            st.session_state.selected = -1  # -1 = no answer given

    # ── Top bar ────────────────────────────────────────────────────────────────
    col_back, col_score = st.columns([3, 1])
    with col_back:
        if st.button(f"← {sub['icon']} {sub['label']}"):
            go("subjects"); st.rerun()
    with col_score:
        st.markdown(f"<div style='text-align:right;padding-top:8px;color:#666'>Score: {st.session_state.score}</div>", unsafe_allow_html=True)

    # ── Timer bar ──────────────────────────────────────────────────────────────
    if pct_left > 0.4:
        bar_color   = "#48BB78"
        text_cls    = "timer-text-normal"
        timer_icon  = "⏱️"
    elif pct_left > 0.15:
        bar_color   = "#ED8936"
        text_cls    = "timer-text-warn"
        timer_icon  = "⚠️"
    else:
        bar_color   = "#E53E3E"
        text_cls    = "timer-text-danger"
        timer_icon  = "🔴"

    timer_type = "Calculation subject — 10 min total" if sub["calc_subject"] else "7 min total"
    st.markdown(f"""
    <div class="timer-label">
      <span class="{text_cls}">{timer_icon} &nbsp;{fmt_time(remaining)} remaining</span>
      <span style="font-size:12px;color:#A0AEC0">{timer_type}</span>
    </div>
    <div class="timer-bar-wrap">
      <div class="timer-bar" style="width:{pct_left*100:.1f}%;background:{bar_color}"></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Progress ───────────────────────────────────────────────────────────────
    st.progress(q_idx / total_qs, text=f"Question {q_idx + 1} of {total_qs}")
    st.markdown("")

    # ── Question ───────────────────────────────────────────────────────────────
    calc_badge = '<span class="calc-badge">📊 Calculation Subject</span>' if sub["calc_subject"] else ""
    st.markdown(f"<p style='font-size:1.15rem;font-weight:500;line-height:1.6'>{q['q']}{calc_badge}</p>", unsafe_allow_html=True)
    st.markdown("")

    # ── Options ────────────────────────────────────────────────────────────────
    is_timed_out = st.session_state.timed_out

    if not st.session_state.locked:
        for i, opt in enumerate(q["opts"]):
            if st.button(f"{LABELS[i]})  {opt}", key=f"opt_{i}", use_container_width=True):
                st.session_state.selected = i
                st.session_state.locked   = True
                if i == q["a"]:
                    st.session_state.score += 1
                st.rerun()
    else:
        chosen = st.session_state.selected

        if is_timed_out and chosen == -1:
            st.markdown('<div class="timeout-badge">⏰ Time\'s up! Subject timer expired. Correct answers are shown below.</div>', unsafe_allow_html=True)

        for i, opt in enumerate(q["opts"]):
            lbl = LABELS[i]
            if is_timed_out and chosen == -1:
                # No answer given — just reveal correct
                if i == q["a"]:
                    st.markdown(f'<div class="opt-reveal">→ {lbl})&nbsp; {opt}&nbsp;<em>(correct answer)</em></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="opt-timeout">&nbsp;&nbsp;{lbl})&nbsp; {opt}</div>', unsafe_allow_html=True)
            else:
                if i == q["a"] and i == chosen:
                    st.markdown(f'<div class="opt-correct">✓ {lbl})&nbsp; {opt}</div>', unsafe_allow_html=True)
                elif i == chosen:
                    st.markdown(f'<div class="opt-wrong">✗ {lbl})&nbsp; {opt}</div>', unsafe_allow_html=True)
                elif i == q["a"]:
                    st.markdown(f'<div class="opt-reveal">→ {lbl})&nbsp; {opt}&nbsp;<em>(correct answer)</em></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="opt-neutral">&nbsp;&nbsp;{lbl})&nbsp; {opt}</div>', unsafe_allow_html=True)

        st.markdown("")

        if not is_timed_out or chosen != -1:
            if chosen == q["a"]:
                st.success("Correct! Well done. ✅")
            else:
                st.error(f"Incorrect. The right answer was **{LABELS[q['a']]}) {q['opts'][q['a']]}**")

        st.markdown("")
        is_last = q_idx + 1 >= total_qs
        btn_label = "See Results →" if is_last else ("Next Question →" if not is_timed_out else "Skip to Results →")

        if st.button(btn_label, use_container_width=True, type="primary"):
            if is_last or is_timed_out:
                st.session_state.subject_scores[sub["id"]] = st.session_state.score
                go("result", active_subject=sub["id"])
            else:
                st.session_state.q_idx    += 1
                st.session_state.selected  = None
                st.session_state.locked    = False
                # NOTE: subject_timer_start is NOT reset — timer continues across all questions
            st.rerun()

    # Auto-refresh every second while timer is live
    if not st.session_state.locked:
        time.sleep(1)
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 4 — Subject Result
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "result":
    sub   = get_subject(st.session_state.active_subject)
    score = st.session_state.subject_scores.get(sub["id"], 0)
    total = len(sub["questions"])
    pct   = round(score / total * 100)

    st.markdown(f"<h2 style='text-align:center'>{sub['icon']} {sub['label']} — Complete</h2>", unsafe_allow_html=True)
    st.markdown("")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="sum-card"><div class="sum-num" style="color:{sub["color"]}">{score}/{total}</div><div class="sum-lbl">Score</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="sum-card"><div class="sum-num" style="color:{sub["color"]}">{pct}%</div><div class="sum-lbl">Percentage</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="sum-card"><div class="sum-num" style="color:#E24B4A">{total - score}</div><div class="sum-lbl">Missed</div></div>', unsafe_allow_html=True)

    st.markdown("")
    st.progress(score / total)
    st.markdown("")
    st.info(get_grade(pct))
    st.markdown("")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 Retry Subject", use_container_width=True):
            go("quiz", active_subject=sub["id"], q_idx=0, score=0,
               selected=None, locked=False, timed_out=False,
               subject_timer_start=time.time())
            st.rerun()
    with c2:
        if st.button("📚 All Subjects", use_container_width=True, type="primary"):
            go("subjects"); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 5 — Overall Results
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "overall":
    if st.button("← Back to Subjects"):
        go("subjects"); st.rerun()

    st.markdown("## 📊 Overall Results")
    st.markdown("")

    all_scores  = st.session_state.subject_scores
    attempted   = len(all_scores)
    total_score = sum(all_scores.values())
    total_q     = attempted * 10
    overall_pct = round(total_score / total_q * 100) if total_q else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="sum-card"><div class="sum-num">{total_score}/{total_q}</div><div class="sum-lbl">Total Score</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="sum-card"><div class="sum-num">{overall_pct}%</div><div class="sum-lbl">Overall %</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="sum-card"><div class="sum-num">{attempted}/{len(SUBJECTS)}</div><div class="sum-lbl">Subjects Done</div></div>', unsafe_allow_html=True)

    st.markdown("")
    st.markdown("### Subject Breakdown")

    for sub in SUBJECTS:
        sc = all_scores.get(sub["id"])
        if sc is not None:
            sp = round(sc / 10 * 100)
            ca, cb = st.columns([4, 1])
            with ca:
                calc_tag = " 📊" if sub["calc_subject"] else ""
                st.markdown(f"**{sub['icon']} {sub['label']}{calc_tag}**")
                st.progress(sc / 10)
            with cb:
                st.markdown(f"<div style='text-align:right;padding-top:20px;color:{sub['color']};font-weight:500'>{sc}/10 ({sp}%)</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"**{sub['icon']} {sub['label']}** — *Not attempted*")

    st.markdown("")
    st.info(get_grade(overall_pct))
    st.markdown("")

    if st.button("🔄 Start Over", use_container_width=True, type="primary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
