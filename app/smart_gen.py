import random

# ---------- helpers ----------
import random
import re

def _digits_prefix(code: str, n: int):
    # خذ أرقام الكود فقط (مفيد لـ CPT مثل 0010T)
    s = re.sub(r"[^0-9]", "", (code or "").strip())
    return s[:n]

def _icd_prefix(code: str, n: int):
    # ICD غالباً يبدأ بحرف + أرقام: E11.9 -> نستخدم أول n بدون نقاط
    s = (code or "").strip().replace(".", "")
    return s[:n]

def _pick_distractors(records, correct_code, difficulty, code_type):
    pool = [r for r in records if r["code"] != correct_code]
    if len(pool) < 3:
        return random.sample(records, min(3, len(records)))

    difficulty = difficulty if difficulty in ("easy", "medium", "hard") else "easy"

    if difficulty == "easy":
        return random.sample(pool, 3)

    if code_type == "icd10":
        # Medium: نفس أول حرف, Hard: نفس أول حرف + رقم
        if difficulty == "medium":
            pref = _icd_prefix(correct_code, 1)
            same = [r for r in pool if _icd_prefix(r["code"], 1) == pref]
            use = same if len(same) >= 3 else pool
            return random.sample(use, 3)
        else:
            pref = _icd_prefix(correct_code, 2)
            same = [r for r in pool if _icd_prefix(r["code"], 2) == pref]
            use = same if len(same) >= 3 else pool
            return random.sample(use, 3)

    # CPT
    if difficulty == "medium":
        pref = _digits_prefix(correct_code, 3)
        same = [r for r in pool if _digits_prefix(r["code"], 3) == pref]
        use = same if len(same) >= 3 else pool
        return random.sample(use, 3)
    else:  # hard
        pref = _digits_prefix(correct_code, 4)
        same = [r for r in pool if _digits_prefix(r["code"], 4) == pref]
        use = same if len(same) >= 3 else pool
        return random.sample(use, 3)

    # CPT: medium same first char, hard same first 2 chars (best effort)
    if difficulty == "medium":
        pref = _prefix(correct_code, 1)
        same = [r for r in pool if _prefix(r["code"], 1) == pref]
        use = same if len(same) >= 3 else pool
        return random.sample(use, 3)
    else:  # hard
        pref = _prefix(correct_code, 2)
        same = [r for r in pool if _prefix(r["code"], 2) == pref]
        use = same if len(same) >= 3 else pool
        return random.sample(use, 3)

def _prompt_text(description, lang):
    if lang == "ar":
        return f"ما هو الكود الصحيح للوصف التالي؟\n{description}"
    return f"Which code best matches the following description?\n{description}"

# ---------- smart MCQ ----------
def generate_smart_mcq(df, n_questions=10, lang="en", difficulty="easy", code_type="cpt"):
    records = df[["code", "description"]].dropna().to_dict("records")
    records = [r for r in records if str(r["code"]).strip() and str(r["description"]).strip()]
    if len(records) < 10:
        return []

    difficulty = difficulty if difficulty in ("easy", "medium", "hard") else "easy"

    questions = []
    for _ in range(n_questions):
        correct = random.choice(records)
        wrongs = _pick_distractors(records, correct["code"], difficulty, code_type)

        options = [correct["code"]] + [w["code"] for w in wrongs]
        random.shuffle(options)

        questions.append({
            "prompt": _prompt_text(correct["description"], lang),
            "options": options,
            "answer": correct["code"],
            "difficulty": difficulty
        })

    return questions

# ---------- Case-based ----------
_CASE_TEMPLATES = {
    "en": [
        "A {age}-year-old {sex} presents for follow-up. The key finding is: {desc}. Select the most appropriate code.",
        "In an outpatient setting, a {age}-year-old {sex} is evaluated. Diagnosis/procedure: {desc}. Choose the correct code.",
        "Clinical scenario: {age}-year-old {sex}. Primary item: {desc}. What is the correct code?"
    ],
    "ar": [
        "حالة سريرية: {sex} عمره/عمرها {age} سنة يراجع للمتابعة. التشخيص/الإجراء: {desc}. اختر الكود الأنسب.",
        "في العيادة: {sex} عمره/عمرها {age} سنة. الوصف الأساسي: {desc}. ما هو الكود الصحيح؟",
        "سيناريو: {sex} {age} سنة. العنصر الرئيسي: {desc}. اختر الكود الصحيح."
    ]
}

def generate_case_mcq(df, n_questions=8, lang="en", difficulty="easy", code_type="icd10"):
    records = df[["code", "description"]].dropna().to_dict("records")
    records = [r for r in records if str(r["code"]).strip() and str(r["description"]).strip()]
    if len(records) < 10:
        return []

    difficulty = difficulty if difficulty in ("easy", "medium", "hard") else "easy"

    ages = [19, 22, 28, 35, 41, 50, 58, 66]
    sexes_en = ["male", "female"]
    sexes_ar = ["ذكر", "أنثى"]

    questions = []
    for _ in range(n_questions):
        correct = random.choice(records)
        wrongs = _pick_distractors(records, correct["code"], difficulty, code_type)

        options = [correct["code"]] + [w["code"] for w in wrongs]
        random.shuffle(options)

        age = random.choice(ages)
        if lang == "ar":
            sex = random.choice(sexes_ar)
            tpl = random.choice(_CASE_TEMPLATES["ar"])
        else:
            sex = random.choice(sexes_en)
            tpl = random.choice(_CASE_TEMPLATES["en"])

        prompt = tpl.format(age=age, sex=sex, desc=correct["description"])

        questions.append({
            "prompt": prompt,
            "options": options,
            "answer": correct["code"],
            "difficulty": difficulty,
            "case": True
        })

    return questions
