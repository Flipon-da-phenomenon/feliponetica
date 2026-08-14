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

    # =====================================================
    # WORD-SPECIFIC PRONUNCIATION CORRECTIONS
    # =====================================================

    # "with" uses the voiceless TH sound in Feliponetica
    # with → W IH TH
    for i, phone in enumerate(phonemes):

        clean_phone = re.sub(r"\d", "", phone)

        if clean_phone == "DH":

            previous_1 = ""
            previous_2 = ""

            if i > 0:
                previous_1 = re.sub(r"\d", "", phonemes[i - 1])

            if i > 1:
                previous_2 = re.sub(r"\d", "", phonemes[i - 2])

            if previous_2 == "W" and previous_1 == "IH":
                phonemes[i] = "TH"

    converted = []

    i = 0

    while i < len(phonemes):

        phone = phonemes[i]

        # =================================================
        # KEEP SPACES
        # =================================================

        if phone == " ":
            converted.append(" ")
            i += 1
            continue

        # =================================================
        # KEEP PUNCTUATION
        # =================================================

        if not re.match(r"^[A-Z]+[0-2]?$", phone):
            converted.append(phone)
            i += 1
            continue

        # Remove stress number
        phone = re.sub(r"\d", "", phone)

        # Get next phoneme
        next_phone = ""

        if i + 1 < len(phonemes):
            next_phone = re.sub(
                r"\d", "",
                phonemes[i + 1]
            )

        # Get phoneme after next
        after_next_phone = ""

        if i + 2 < len(phonemes):
            after_next_phone = re.sub(
                r"\d", "",
                phonemes[i + 2]
            )

                # =================================================
        # Y + UW + AH + L
        # =================================================

        # fuel → fiuol

        if (
            phone == "Y"
            and next_phone == "UW"
            and after_next_phone == "AH"
        ):

            if i + 3 < len(phonemes):
                after_ah_phone = re.sub(
                    r"\d", "",
                    phonemes[i + 3]
                )

                if after_ah_phone == "L":
                    converted.append("iuol")
                    i += 4
                    continue


        # =================================================
        # Y + UW + L
        # =================================================
        #
        # mule → miuol
        # fuel → fiuol
        #
        # Y UW L → iuol

        if (
            phone == "Y"
            and next_phone == "UW"
            and after_next_phone == "L"
        ):

            converted.append("iuol")

            i += 3
            continue


        # =================================================
        # Y + UW
        # =================================================
        #
        # few → fiu
        # future → fiuchr
        # fusion → fiu...

        if phone == "Y" and next_phone == "UW":

            converted.append("iu")

            i += 2
            continue

        # =================================================
        # AO + R
        # =================================================
        #
        # north
        # core
        # bore
        # store
        # chore
        # lore
        # more
        #
        # AO R → o r

        if phone == "AO" and next_phone == "R":

            converted.append("or")

            i += 2
            continue

        # =================================================
        # NG + K
        # =================================================
        #
        # think
        # thank
        # drink
        # bank
        #
        # NG K → n k

        if phone == "NG" and next_phone == "K":

            converted.append("nk")

            i += 2
            continue

        # =================================================
        # FINAL L RULE
        # =================================================
        #
        # UW + L → uol
        # IY + L → iol
        # EY + L → eiol
        # AY + L → aiol
        # OY + L → oiol
        #
        # Examples:
        #
        # full   → fuol
        # feel   → fiol
        # school → skuol
        # male   → meiol
        # tail   → teiol
        # oil    → oiol
        #
        # IH + L is NOT changed.
        #
        # fill → fiʰl
        # hill → hiʰl

        if (
            phone in ["UW", "IY", "EY", "AY", "OY"]
            and next_phone == "L"
        ):

            vowel = CMU_TO_FELIPONETICA.get(
                phone,
                phone
            )

            converted.append(vowel + "ol")

            i += 2
            continue

        # =================================================
        # NORMAL CMU → FELIPONETICA
        # =================================================

        converted.append(
            CMU_TO_FELIPONETICA.get(
                phone,
                phone
            )
        )

        i += 1

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