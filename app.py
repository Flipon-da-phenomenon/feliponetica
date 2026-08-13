import nltk
import re

from flask import Flask, render_template, request
from g2p_en import G2p


# ============================================================
# NLTK DATA
# ============================================================

NLTK_DATA_PATH = "/opt/render/nltk_data"

nltk.data.path.insert(0, NLTK_DATA_PATH)

nltk.download(
    "averaged_perceptron_tagger_eng",
    download_dir=NLTK_DATA_PATH
)

nltk.download(
    "cmudict",
    download_dir=NLTK_DATA_PATH
)


g2p = G2p()

app = Flask(__name__)


# ============================================================
# FELIPONETICA
# ============================================================

CMU_TO_FELIPONETICA = {

    # Vowels
    "AA": "a˂",
    "AE": "aʰ",
    "AH": "uʰ",
    "AO": "a˂",
    "AW": "au",
    "AY": "ai",
    "EH": "e",
    "ER": "er",
    "EY": "ei",
    "IH": "iʰ",
    "IY": "i",
    "OW": "ou",
    "OY": "oi",
    "UH": "uᶠ",
    "UW": "u",

    # Stops
    "P": "p",
    "B": "b",
    "T": "t",
    "D": "d",
    "K": "k",
    "G": "g",

    # Fricatives
    "F": "f",
    "V": "v",
    "TH": "thˢ",
    "DH": "thᶻ",
    "S": "s",
    "Z": "z",
    "SH": "sh",
    "ZH": "shᶻ",
    "HH": "j",

    # Affricates
    "CH": "ch",
    "JH": "shᶻ",

    # Nasals
    "M": "m",
    "N": "n",
    "NG": "ng",

    # Liquids
    "L": "l",
    "R": "r",

    # Glides
    "W": "w",
    "Y": "ll",
}


def convert_to_feliponetica(text):

    phonemes = g2p(text)

    converted = []

    for phone in phonemes:

        # Keep spaces
        if phone == " ":
            converted.append(" ")
            continue

        # Keep punctuation
        if not re.match(r"^[A-Z]+[0-2]?$", phone):
            converted.append(phone)
            continue

        # Remove stress number
        phone = re.sub(r"\d", "", phone)

        # Convert CMU phoneme
        converted.append(
            CMU_TO_FELIPONETICA.get(phone, phone)
        )

    return "".join(converted)


# ============================================================
# HOME
# ============================================================

@app.route('/')
def home():
    return render_template('index.html')


# ============================================================
# FELIPONETICA
# ============================================================

@app.route('/feliponetica', methods=['GET', 'POST'])
def feliponetica():

    result = None
    user_input = ""

    if request.method == 'POST':

        user_input = request.form.get(
            'transcript_text',
            ''
        ).strip()

        if user_input:
            result = convert_to_feliponetica(user_input)

    return render_template(
        'feliponetica.html',
        result=result,
        user_input=user_input
    )


# ============================================================
# VOCABULARY DRILL
# ============================================================

@app.route('/vocab_drill')
def vocab():
    return render_template('vocab_drill.html')


# ============================================================
# LESSONS
# ============================================================

@app.route('/lessons')
def lessons():
    return render_template('lessons.html')


# ============================================================
# COURSE
# ============================================================

@app.route('/course')
def course():
    return render_template('course.html')


# ============================================================
# ABOUT
# ============================================================

@app.route('/about')
def about():
    return render_template('about.html')


# ============================================================
# LIVE CLASSES
# ============================================================

@app.route('/live-classes')
def live_classes():
    return render_template('live_classes.html')


# ============================================================
# CONTACT
# ============================================================

@app.route('/contact')
def contact():
    return render_template('contact.html')


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)