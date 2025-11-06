import streamlit as st
import pandas as pd

# -----------------------------------
# Init session state
# -----------------------------------
if "step" not in st.session_state:
    st.session_state.step = 1

if "age" not in st.session_state:
    st.session_state.age = 25

# load lookup
@st.cache_data
def load_dasha():
    return pd.read_excel("dasha_lookup.xlsx", engine="openpyxl")

df = load_dasha()

zodiacs = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]
zodiac_to_num = {z: i for i, z in enumerate(zodiacs)}

# convert zodiac + degree + minute → absolute minute index
def to_abs_minutes(sign, deg, minute):
    sign_offset = zodiac_to_num[sign] * 30 * 60   # 30° * 60min
    return sign_offset + deg*60 + minute

# -----------------------------------
# STEP 1 — Moon1/Moon2 & Age Input
# -----------------------------------
if st.session_state.step == 1:

    st.title("Dasha Timefinder")
    st.caption("Enter your sidereal Moon range & current age")

    with st.form("moon_form"):
        col1, col2 = st.columns(2)

        # Moon start
        with col1:
            st.subheader("Moon1 (00:00)")
            z1 = st.selectbox("Sign", zodiacs, key="z1")
            d1 = st.selectbox("Degree", range(30), key="d1")
            m1 = st.selectbox("Minute", range(60), key="m1")

        # Moon end
        with col2:
            st.subheader("Moon2 (23:59)")
            z2 = st.selectbox("Sign ", zodiacs, key="z2")
            d2 = st.selectbox("Degree ", range(30), key="d2")
            m2 = st.selectbox("Minute ", range(60), key="m2")

        st.write("### Age")
        age = st.slider("Age", 1, 120, value=st.session_state.age)
        st.session_state.age = age

        submit = st.form_submit_button("Continue →")

    # process form
    if submit:
        m1_idx = to_abs_minutes(z1, d1, m1)
        m2_idx = to_abs_minutes(z2, d2, m2)

        # ✅ Pisces → Aries 경계 보정
        if z1.lower() in ["aquarius", "pisces"] and z2.lower() == "aries":
            m2_idx += 21600  # 한 사이클 추가 (12 signs × 1800분)

        df1 = df[df["Minutes"] == m1_idx]
        df2 = df[df["Minutes"] == m2_idx]

        if df1.empty or df2.empty:
            st.error("❌ Moon not found in lookup (degree–minute mismatch).")
        else:
            arc = m2_idx - m1_idx

            # ✅ arc 검사
            if not (660 <= arc <= 900):
                st.error(f"❌ Moon arc {arc} min invalid. Must be 660–900.")
            elif not (10 <= age <= 99):
                st.error("❌ Age must be between 10–99.")
            else:
                # ✅ store internally
                st.session_state.moon1 = m1_idx
                st.session_state.moon2 = m2_idx
                st.session_state.step = 2
                st.rerun()

    st.stop()


# -----------------------------------
# STEP 2 — Q1: Child Emotion
# -----------------------------------
elif st.session_state.step == 2:
    from questions.clinical.child_emotion import Q1_CHILD_EMOTION

    # ✅ Function: get which Dasha appear in this Moon childhood arc
# ✅ Function: extract childhood planets from arc
# ✅ Function: extract childhood planets from arc
    def get_child_planets_in_arc(df, m1, m2):
        if m2 < m1:  # wrap-around case
            segment = pd.concat([
                df[df["Minutes"] >= m1],
                df[df["Minutes"] <= m2]
            ])
        else:
            segment = df[(df["Minutes"] >= m1) & (df["Minutes"] <= m2)]

        # pick unique childhood planets (not boolean)
        planets = segment["Childhood"].dropna().unique().tolist()
        return [p.lower() for p in planets]   # match option id format



    # ✅ Fetch arc-specific Dasha sequence
    child_planets = get_child_planets_in_arc(df, st.session_state.moon1, st.session_state.moon2)
    
    # ✅ Filter Q1 options to only include relevant planets
    filtered_options = [
        opt for opt in Q1_CHILD_EMOTION["options"]
        if opt["id"] in child_planets
    ]


    st.divider()

    # ✅ Styled Question
    question_html = f"""
    <div style="
        font-size: 1.05rem; 
        font-style: italic;
        color: #b04a4a;        /* soft maple red */
        line-height: 1.6;
        margin-bottom: 25px;
        text-align: center;
    ">
    {Q1_CHILD_EMOTION["question"].replace("\n", "<br>")}
    </div>
    """

    st.markdown(question_html, unsafe_allow_html=True)

    st.divider()

    # ✅ If no matching childhood dasha options exist
    if not filtered_options:
        st.warning("해당 월궁 범위에 해당되는 어린 시절 감정 문항이 없습니다.")
        if st.button("Reset"):
            st.session_state.clear()
            st.rerun()
        st.stop()

    # ✅ Show filtered options only
    for opt in filtered_options:
        col_text, col_btn = st.columns([8,1])

        with col_text:
            st.markdown(
                f"""
                <div style="
                    padding: 12px 16px; 
                    border: 1px solid #ddd; 
                    border-radius: 8px; 
                    line-height: 1.55;
                    white-space: pre-line;
                ">
                {opt['text'].replace('\n', '<br>')}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_btn:
            if st.button("선택", key=f"btn_{opt['id']}"):
                st.session_state.childhood = opt["id"]
                st.session_state.step = 3
                st.rerun()

# -----------------------------------
# STEP 3 — Childhood Relationships
# -----------------------------------
elif st.session_state.step == 3:
    from questions.clinical.childhood_relationships import Q2_CHILDHOOD_RELATIONSHIPS

    st.divider()

    # Filter planets based on moon arc range
    df_arc = df[(df["Minutes"] >= st.session_state.moon1) & (df["Minutes"] <= st.session_state.moon2)]
    child_planets = df_arc["Childhood"].dropna().unique().tolist()
    child_planets = [c.lower() for c in child_planets]  # match question IDs

    # Match question options
    filtered_options = [opt for opt in Q2_CHILDHOOD_RELATIONSHIPS["options"] if opt["id"] in child_planets]

    # Styled question
    question_html = f"""
    <div style="
        font-size: 1.05rem; 
        font-style: italic;
        color: #b04a4a;
        line-height: 1.6;
        margin-bottom: 25px;
        text-align: center;
    ">
    {Q2_CHILDHOOD_RELATIONSHIPS["question"].replace("\n", "<br>")}
    </div>
    """
    st.markdown(question_html, unsafe_allow_html=True)
    st.divider()

    if not filtered_options:
        st.warning("해당 범위에 해당되는 어린 시절 관계감각 문항이 없습니다.")
    else:
        for opt in filtered_options:
            col_text, col_btn = st.columns([8, 1])

            with col_text:
                st.markdown(
                    f"<div style='padding:12px 16px; border:1px solid #ddd; border-radius:8px; line-height:1.55;'>{opt['text'].replace('\n', '<br>')}</div>",
                    unsafe_allow_html=True
                )
            with col_btn:
                if st.button("선택", key=f"rel_{opt['id']}"):
                    st.session_state.child_relationship = opt["id"]
                    st.session_state.step = 4
                    st.rerun()

    if st.button("Reset"):
        st.session_state.clear()
        st.rerun()


# -----------------------------------
# STEP 4 — Subconscious Intro Screen
# -----------------------------------

elif st.session_state.step == 4:
    from questions.subconscious.scn_intro import SUBCONSCIOUS_INTRO

    # Dark mode + text styling (clean version)
    st.markdown("""
    <style>
    /* Dark background and text */
    .block-container {
        background-color: #000 !important;
        color: #e9e9e9 !important;
    }

    /* Story text style */
    .story-text {
        font-size: 1.20rem;
        font-style: italic;
        color: #f7f7f7;
        text-align: center;
        line-height: 1.85;
        padding: 30px 10px;
        max-width: 850px;
        margin-left: auto;
        margin-right: auto;
    }

    /* ✅ Streamlit default button — maple red text */
    div.stButton > button {
        color: #b04a4a !important;   /* maple red */
        font-weight: 600 !important;
        background-color: rgba(255,255,255,0.15) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255,255,255,0.7) !important;
    }

    /* ✅ Hover */
    div.stButton > button:hover {
        color: black !important;
        background-color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)


    # Render story
    story_html = SUBCONSCIOUS_INTRO["body"].replace("\n", "<br>")
    st.markdown(f"<div class='story-text'>{story_html}</div>", unsafe_allow_html=True)

    # Button bottom center
    st.markdown("<div class='bottom-center-btn'>", unsafe_allow_html=True)
    if st.button(SUBCONSCIOUS_INTRO["button_text"], key="sub_next"):
        st.session_state.step = 5
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------
# STEP 5 — SCN_CALL_1: Subconscious Call
# -----------------------------------
elif st.session_state.step == 5:
    from questions.subconscious.scn_call import SCN_CALL_1

    st.markdown(
        f"""
        <div class="story-text">
        {SCN_CALL_1["narrative"].replace("\n", "<br>")}
        </div>
        """, unsafe_allow_html=True
    )

    st.divider()

    # Render choices
    for opt in SCN_CALL_1["options"]:
        col_text, col_btn = st.columns([8, 1])

        with col_text:
            st.markdown(
                f"""
                <div style='
                    padding: 12px 16px;
                    border: 1px solid #444;
                    background-color: rgba(255,255,255,0.07);
                    border-radius: 10px;
                    line-height: 1.6;
                    margin-bottom: 10px;
                    font-style: italic;
                '>
                    {opt['text'].replace("\n", "<br>")}
                </div>
                """, unsafe_allow_html=True
            )

        with col_btn:
            if st.button("선택", key=opt["id"]):
                st.session_state.scn_call = opt["id"]

                # ✅ go to next step
                st.session_state.step = 6  
                st.rerun()

    st.divider()

# -----------------------------------
# STEP 6 — SCN_WHISPER
# -----------------------------------
elif st.session_state.step == 6:
    from questions.subconscious.scn_whisper import SCN_WHISPER_2

    # narrative
    st.markdown(
        f"""
        <div class="story-text">
        {SCN_WHISPER_2["narrative"].replace("\n", "<br>")}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # choices
    for opt in SCN_WHISPER_2["options"]:
        col_text, col_btn = st.columns([8,1])

        with col_text:
            st.markdown(
                f"""
                <div style='
                    padding: 12px 16px;
                    border: 1px solid #444;
                    background-color: rgba(255,255,255,0.07);
                    border-radius: 10px;
                    line-height: 1.6;
                    margin-bottom: 10px;
                    font-style: italic;
                '>
                {opt['text'].replace("\n", "<br>")}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_btn:
            if st.button("선택", key=opt["id"]):
                st.session_state.scn_whisper = opt["id"]
                st.session_state.purushartha_whisper = opt["id"]
                # ✅ go to next step
                st.session_state.step = 7  
                st.rerun()



# -----------------------------------
# STEP 7 — SOUL_ORIGIN
# -----------------------------------
elif st.session_state.step == 7:
    from questions.clinical.soul_origin import Q3_SOUL_ORIGIN

    # narrative
    st.markdown(
        f"""
        <div class="story-text">
        {Q3_SOUL_ORIGIN["question"].replace("\n", "<br>")}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # Filter planets based on moon arc range
    df_arc = df[(df["Minutes"] >= st.session_state.moon1) & (df["Minutes"] <= st.session_state.moon2)]
    child_planets = df_arc["Dasha"].dropna().unique().tolist()
    child_planets = [c.lower() for c in child_planets]  # match question IDs

    # Match question options
    filtered_options = [opt for opt in Q3_SOUL_ORIGIN["options"] if opt["id"] in child_planets]

    if not filtered_options:
        filtered_options = Q3_SOUL_ORIGIN["options"]

    for opt in filtered_options:
        col_text, col_btn = st.columns([8,1])

        with col_text:
            st.markdown(
                f"""
                <div style='
                    padding: 12px 16px;
                    border: 1px solid #444;
                    background-color: rgba(255,255,255,0.07);
                    border-radius: 10px;
                    line-height: 1.6;
                    margin-bottom: 10px;
                    font-style: italic;
                '>
                {opt['text'].replace("\n", "<br>")}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_btn:
            if st.button("선택", key=opt["id"]):
                st.session_state.soul_origin = opt["id"]
                st.session_state.step = 8
                st.rerun()


# -----------------------------------
# STEP 8 — Q4: SOLITUDE
# -----------------------------------
elif st.session_state.step == 8:
    from questions.clinical.solitude import Q4_SOLITUDE

    # ✅ Function: get which Dasha appear in this Moon childhood arc
# ✅ Function: extract childhood planets from arc
# ✅ Function: extract childhood planets from arc
    def get_nakshatra_planets_in_arc(df, m1, m2):
        if m2 < m1:  # wrap-around case
            segment = pd.concat([
                df[df["Minutes"] >= m1],
                df[df["Minutes"] <= m2]
            ])
        else:
            segment = df[(df["Minutes"] >= m1) & (df["Minutes"] <= m2)]

        # pick unique childhood planets (not boolean)
        planets = segment["Dasha"].dropna().unique().tolist()
        return [p.lower() for p in planets]   # match option id format



    # ✅ Fetch arc-specific Dasha sequence
    nakshatra_planets = get_nakshatra_planets_in_arc(df, st.session_state.moon1, st.session_state.moon2)
    
    # ✅ Filter Q1 options to only include relevant planets
    filtered_options = [
        opt for opt in Q4_SOLITUDE["options"]
        if opt["id"] in nakshatra_planets
    ]


    st.divider()

    # ✅ Styled Question
    question_html = f"""
    <div style="
        font-size: 1.05rem; 
        font-style: italic;
        color: #b04a4a;        /* soft maple red */
        line-height: 1.6;
        margin-bottom: 25px;
        text-align: center;
    ">
    {Q4_SOLITUDE["question"].replace("\n", "<br>")}
    </div>
    """

    st.markdown(question_html, unsafe_allow_html=True)

    st.divider()

    # ✅ If no matching childhood dasha options exist
    if not filtered_options:
        st.warning("해당 월궁 범위에 해당되는 문항이 없습니다.")
        if st.button("Reset"):
            st.session_state.clear()
            st.rerun()
        st.stop()

    # ✅ Show filtered options only
    for opt in filtered_options:
        col_text, col_btn = st.columns([8,1])

        with col_text:
            st.markdown(
                f"""
                <div style="
                    padding: 12px 16px; 
                    border: 1px solid #ddd; 
                    border-radius: 8px; 
                    line-height: 1.55;
                    white-space: pre-line;
                ">
                {opt['text'].replace('\n', '<br>')}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_btn:
            if st.button("선택", key=f"btn_{opt['id']}"):
                st.session_state.solitude = opt["id"]
                st.session_state.step = 9
                st.rerun()

# -----------------------------------
# STEP 9 — SCN_RIGHTEOUS
# -----------------------------------
elif st.session_state.step == 9:
    from questions.subconscious.scn_righteous import SCN_RIGHTEOUS_3

    # narrative
    st.markdown(
        f"""
        <div class="story-text">
        {SCN_RIGHTEOUS_3["narrative"].replace("\n", "<br>")}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()


    # ✅ STEP 9 only — light grey background theme
    st.markdown("""
        <style>
        .block-container {
            background-color: #f3f3f3 !important;  /* light grey */
            color: #222 !important;               /* dark text */
        }
        .story-text {
            font-size: 1.1rem;
            font-style: italic;
            color: #5a3a3a; /* subtle warm deep brown-red tone */
            text-align: center;
            line-height: 1.85;
            padding: 30px 10px;
            max-width: 850px;
            margin-left: auto;
            margin-right: auto;
        }
        /* Button style override */
        .stButton>button {
            background-color: rgba(255, 255, 255, 0.5) !important;
            border: 1px solid #666 !important;
            color: #b04a4a !important;
            font-weight: 600;
            border-radius: 8px !important;
        }
        .stButton>button:hover {
            background-color: #fff !important;
            color: #000 !important;
        }
        </style>
    """, unsafe_allow_html=True)


    st.divider()

    # choices
    for opt in SCN_RIGHTEOUS_3["options"]:
        col_text, col_btn = st.columns([8,1])

        with col_text:
            st.markdown(
                f"""
                <div style='
                    padding: 12px 16px;
                    border: 1px solid #444;
                    background-color: rgba(255,255,255,0.07);
                    border-radius: 10px;
                    line-height: 1.6;
                    margin-bottom: 10px;
                    font-style: italic;
                '>
                {opt['text'].replace("\n", "<br>")}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_btn:
            if st.button("선택", key=opt["id"]):
                st.session_state.scn_righteous = opt["id"]
                st.session_state.purushartha_righteous = opt["id"]
                # ✅ go to next step
                st.session_state.step = 10  
                st.rerun()

# -----------------------------------
# STEP 10 — SCN_CONFUSION
# -----------------------------------
elif st.session_state.step == 10:
    from questions.subconscious.scn_confusion import SCN_CONFUSION_4

    # ✅ Dark subconscious theme return
    st.markdown("""
        <style>
        .block-container {
            background-color: #000 !important;
            color: #eaeaea !important;
        }
        .story-text {
            font-size: 1.1rem;
            font-style: italic;
            color: #e6e6e6;
            text-align: center;
            line-height: 1.9;
            padding: 32px 14px;
            max-width: 860px;
            margin-left: auto;
            margin-right: auto;
        }
        .stButton>button {
            background-color: rgba(255,255,255,0.08) !important;
            border: 1px solid rgba(255,255,255,0.55) !important;
            color: #b04a4a !important;
            font-weight: 600;
            border-radius: 8px !important;
            padding: 8px 18px;
        }
        .stButton>button:hover {
            background-color: white !important;
            color: black !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # narrative text
    st.markdown(
        f"""
        <div class="story-text">
        {SCN_CONFUSION_4["narrative"].replace("\n", "<br>")}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # options
    for opt in SCN_CONFUSION_4["options"]:
        col_text, col_btn = st.columns([8,1])

        with col_text:
            st.markdown(
                f"""
                <div style='
                    padding: 12px 16px;
                    border: 1px solid #555;
                    background-color: rgba(255,255,255,0.05);
                    border-radius: 10px;
                    line-height: 1.65;
                    margin-bottom: 12px;
                    font-style: italic;
                    color: #e9e9e9;
                '>
                {opt['text'].replace("\\n", "<br>")}
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col_btn:
            if st.button("선택", key=f"conf_{opt['id']}"):
                st.session_state.scn_confusion = opt["id"]
                st.session_state.step = 11
                st.rerun()

# -----------------------------------
# STEP 11 — LIFE SHIFT TIMING
# -----------------------------------
elif st.session_state.step == 11:
    from questions.clinical.life_shift import Q5_LIFE_SHIFT

    st.markdown(
        f"""
        <div style="font-size:1.1rem; font-style:italic; color:#b04a4a; line-height:1.6; text-align:center;">
            {Q5_LIFE_SHIFT["question"].replace("\n","<br>")}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("")

    # Filter moon arc section
    df_arc = df[(df["Minutes"] >= st.session_state.moon1) & (df["Minutes"] <= st.session_state.moon2)]

    # Columns to reference
    col_map = {
        "child": "Child",
        "puberty_start": "Puberty",
        "puberty": "Puberty",
        "post_puberty": "P_Puberty",
        "20s": "20's",
        "no_shift": "Noshift_Max"
    }

    user_age = st.session_state.age

    # Build filtered option list
    valid_opts = []
    for opt in Q5_LIFE_SHIFT["options"]:
        opt_id = opt["id"]

        # ✅ Turmoil은 항상 포함
        if opt_id == "turmoil":
            valid_opts.append(opt)
            continue

        col = col_map.get(opt_id)  # 안전하게 get()으로 조회

        if not col:
            continue

        if col == "Noshift_Max":
            max_val = df_arc[col].dropna().max()
            if pd.notna(max_val) and user_age <= max_val:
                valid_opts.append(opt)
        else:
            if df_arc[col].astype(str).str.upper().isin(["TRUE", "YES", "1"]).any():
                valid_opts.append(opt)


    st.divider()

    # Display valid options
    for opt in valid_opts:
        col_txt, col_btn = st.columns([8,1])

        with col_txt:
            st.markdown(
                f"""
                <div style='padding:12px 16px; border:1px solid #ddd; border-radius:8px; line-height:1.55; margin-bottom:10px;'>
                {opt['text']}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_btn:
            if st.button("선택", key=f"lifeshift_{opt['id']}"):
                st.session_state.life_shift_timing = opt["id"]

                # Routing logic
                if opt["id"] in ["child","puberty_start","puberty"]:
                    st.session_state.step = 12      # Q6 life shift mood step
                else:
                    st.session_state.step = 13      # abyss branch step

                st.rerun()




# -----------------------------------
# STEP 12 — LIFE SHIFT MOOD
# -----------------------------------
elif st.session_state.step == 12:
    from questions.clinical.life_shift_mood import get_shift_mood_question

    q5_choice = st.session_state.get("life_shift_timing")

    # determine stage from Q5
    mood_stage = "child" if q5_choice == "child" else "teen"
    q6 = get_shift_mood_question(mood_stage)

    # 🎯 Filter options by Dasha in current Moon arc
    df_arc = df[(df["Minutes"] >= st.session_state.moon1) &
                (df["Minutes"] <= st.session_state.moon2)]
    dashas = df_arc["Dasha"].dropna().unique().tolist()
    dashas = [d.lower() for d in dashas]

    # 기본 dasha 필터링
    filtered_opts = [opt for opt in q6["options"] if opt["id"].lower() in dashas]

    # “잘 모르겠다” 추가 옵션 (항상 표시)
    unknown_opt = {
        "id": "unknown",
        "text": (
            "위 항목 중에서는 잘 모르겠다.\n"
            "분명 변화는 있었던 것 같은데,\n"
            "딱 맞는 느낌은 떠오르지 않는다."
        )
    }
    filtered_opts.append(unknown_opt)

    # Question text
    st.markdown(
        f"""
        <div class="story-text">
        {q6["question"].replace("\n","<br>")}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.divider()

    # Render options
    for opt in filtered_opts:
        col_text, col_btn = st.columns([8, 1])

        with col_text:
            st.markdown(
                f"""
                <div style='
                    padding: 12px 16px;
                    border: 1px solid #444;
                    background-color: rgba(255,255,255,0.07);
                    border-radius: 10px;
                    line-height: 1.6;
                    margin-bottom: 10px;
                    font-style: italic;
                '>
                {opt['text'].replace("\\n","<br>")}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_btn:
            if st.button("선택", key=f"q6_{opt['id']}"):
                st.session_state.life_shift_mood = opt["id"]

                st.session_state.step = 13
                st.rerun()


# -----------------------------------
# STEP 13 — SCN_ABYSS
# -----------------------------------
elif st.session_state.step == 13:
    from questions.subconscious.scn_abyss import SCN_ABYSS_5

    # ✅ Dark subconscious theme return
    st.markdown("""
        <style>
        .block-container {
            background-color: #000 !important;
            color: #eaeaea !important;
        }
        .story-text {
            font-size: 1.1rem;
            font-style: italic;
            color: #e6e6e6;
            text-align: center;
            line-height: 1.9;
            padding: 32px 14px;
            max-width: 860px;
            margin-left: auto;
            margin-right: auto;
        }
        .stButton>button {
            background-color: rgba(255,255,255,0.08) !important;
            border: 1px solid rgba(255,255,255,0.55) !important;
            color: #b04a4a !important;
            font-weight: 600;
            border-radius: 8px !important;
            padding: 8px 18px;
        }
        .stButton>button:hover {
            background-color: white !important;
            color: black !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # narrative text
    st.markdown(
        f"""
        <div class="story-text">
        {SCN_ABYSS_5["narrative"].replace("\n", "<br>")}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # options
    for opt in SCN_ABYSS_5["options"]:
        col_text, col_btn = st.columns([8,1])

        with col_text:
            st.markdown(
                f"""
                <div style='
                    padding: 12px 16px;
                    border: 1px solid #555;
                    background-color: rgba(255,255,255,0.05);
                    border-radius: 10px;
                    line-height: 1.65;
                    margin-bottom: 12px;
                    font-style: italic;
                    color: #e9e9e9;
                '>
                {opt['text'].replace("\n", "<br>")}
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col_btn:
            if st.button("선택", key=f"conf_{opt['id']}"):
                st.session_state.scn_abyss = opt["id"]
                st.session_state.purushartha_abyss = opt["id"]
                st.session_state.step = 14
                st.rerun() 

# -----------------------------------
# STEP 14 — SCN_TEMPTATION
# -----------------------------------
elif st.session_state.step == 14:
    from questions.subconscious.scn_temptation import SCN_TEMPTATION_6

    # narrative
    st.markdown(
        f"""
        <div class="story-text">
        {SCN_TEMPTATION_6["narrative"].replace("\n", "<br>")}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()


    st.markdown("""
        <style>
        .block-container {
            background-color: #f3f3f3 !important;  /* light grey */
            color: #222 !important;               /* dark text */
        }
        .story-text {
            font-size: 1.1rem;
            font-style: italic;
            color: #5a3a3a; /* subtle warm deep brown-red tone */
            text-align: center;
            line-height: 1.85;
            padding: 30px 10px;
            max-width: 850px;
            margin-left: auto;
            margin-right: auto;
        }
        /* Button style override */
        .stButton>button {
            background-color: rgba(255, 255, 255, 0.5) !important;
            border: 1px solid #666 !important;
            color: #b04a4a !important;
            font-weight: 600;
            border-radius: 8px !important;
        }
        .stButton>button:hover {
            background-color: #fff !important;
            color: #000 !important;
        }
        </style>
    """, unsafe_allow_html=True)


    st.divider()

    # choices
    for opt in SCN_TEMPTATION_6["options"]:
        col_text, col_btn = st.columns([8,1])

        with col_text:
            st.markdown(
                f"""
                <div style='
                    padding: 12px 16px;
                    border: 1px solid #444;
                    background-color: rgba(255,255,255,0.07);
                    border-radius: 10px;
                    line-height: 1.6;
                    margin-bottom: 10px;
                    font-style: italic;
                '>
                {opt['text'].replace("\n", "<br>")}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_btn:
            if st.button("선택", key=opt["id"]):
                st.session_state.scn_temptation = opt["id"]
                # ✅ go to next step
                st.session_state.step = 15  
                st.rerun()


# -----------------------------------
# STEP 15 — LETTING_GO
# -----------------------------------
elif st.session_state.step == 15:
    from questions.subconscious.letting_go import Q7_LETTING_GO

    # narrative
    st.markdown(
        f"""
        <div class="story-text">
        {Q7_LETTING_GO["question"].replace("\n", "<br>")}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # choices
    for opt in Q7_LETTING_GO["options"]:
        col_text, col_btn = st.columns([8,1])

        with col_text:
            st.markdown(
                f"""
                <div style='
                    padding: 12px 16px;
                    border: 1px solid #444;
                    background-color: rgba(255,255,255,0.07);
                    border-radius: 10px;
                    line-height: 1.6;
                    margin-bottom: 10px;
                    font-style: italic;
                '>
                {opt['text'].replace("\n", "<br>")}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_btn:
            if st.button("선택", key=opt["id"]):
                st.session_state.purushartha = opt["id"]
                # ✅ go to next step
                st.session_state.step = 16 
                st.rerun()

# -----------------------------------
# STEP 16 — Epilogue (Light Mode Return)
# -----------------------------------

elif st.session_state.step == 16:
    from questions.subconscious.scn_epilogue import SUBCONSCIOUS_EPILOGUE

    # Style for epilogue — return to light theme
    st.markdown("""
    <style>
    /* Reset background (return to daylight / conscious world) */
    .block-container {
        background-color: #fafafa !important;
        color: #222222 !important;
    }

    /* Story text formatting */
    .story-text {
        font-size: 1.10rem;
        font-style: italic;
        color: #333;
        text-align: center;
        line-height: 1.85;
        padding: 30px 10px;
        max-width: 850px;
        margin-left: auto;
        margin-right: auto;
    }

    /* Button — keep maple red signature */
    div.stButton > button {
        color: #b04a4a !important;
        font-weight: 600 !important;
        background-color: rgba(0,0,0,0.04) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(0,0,0,0.35) !important;
        padding: 8px 18px !important;
    }

    div.stButton > button:hover {
        color: white !important;
        background-color: #b04a4a !important;
        border-color: #b04a4a !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Render epilogue text
    story_html = SUBCONSCIOUS_EPILOGUE["body"].replace("\n", "<br>")
    st.markdown(f"<div class='story-text'>{story_html}</div>", unsafe_allow_html=True)

    # Continue button
    if st.button(SUBCONSCIOUS_EPILOGUE["button_text"], key="sub_next"):
        st.session_state.step = 17
        st.rerun()

# -----------------------------------
# STEP 17 — FINAL SEGMENT SPLIT (Fixed)
# -----------------------------------
elif st.session_state.step == 17:
    import pandas as pd
    import re, ast

    # ===============================
    # 🎨 스타일
    # ===============================
    st.markdown("""
    <style>
    .main-title {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: #111;
        margin-top: 40px;
        margin-bottom: 35px;
    }
    .result-text {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 1.1rem;
        color: #222;
        line-height: 1.9;
        margin-left: 6px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='main-title'>Results Based on User's Input</div>", unsafe_allow_html=True)

    # ===============================
    # 📘 기본 moon arc dataset
    # ===============================
    df_arc = df[(df["Minutes"] >= st.session_state.moon1) &
                (df["Minutes"] <= st.session_state.moon2)].copy()
    df_arc.columns = [str(c).strip().lower() for c in df_arc.columns]

    # ===============================
    # 🧩 유틸
    # ===============================
    def normalize(v):
        return str(v).strip().lower().replace("’","'").replace('"','').replace("`","'")

    def to_list(x):
        if pd.isna(x): return []
        x = normalize(x)
        try:
            if x.startswith('[') and x.endswith(']'):
                return [normalize(v) for v in ast.literal_eval(x)]
        except Exception:
            pass
        parts = re.split(r'[|,\/\s]+', x)
        return [normalize(p) for p in parts if p.strip()]

    def norm_match(x, val):
        return normalize(str(x)) == normalize(str(val))

    # ===============================
    # ① Childhood filter
    # ===============================
    childhood_choice = normalize(st.session_state.get("childhood"))
    if "childhood" in df_arc.columns and childhood_choice:
        df_arc["child_list"] = df_arc["childhood"].apply(to_list)
        df_base = df_arc[df_arc["child_list"].apply(lambda lst: childhood_choice in lst)]
    else:
        df_base = df_arc.copy()

    # ===============================
    # ② Solitude filter (Natal Dasha)
    # ===============================
    solitude_choice = normalize(st.session_state.get("solitude"))
    if "dasha" in df_base.columns and solitude_choice:
        df_base["dasha_norm"] = df_base["dasha"].apply(normalize)
        df_sol = df_base[df_base["dasha_norm"] == solitude_choice]
        if not df_sol.empty:
            df_base = df_sol.copy()

    # ===============================
    # ③ Purushartha 필터
    # ===============================
    puru_counts = {}
    for q in ["whisper", "righteous", "abyss"]:
        choice = st.session_state.get(f"purushartha_{q}")
        if choice:
            puru_counts[choice] = puru_counts.get(choice, 0) + 1

    # ✅ 동점이면 None으로
    if puru_counts:
        max_count = max(puru_counts.values())
        if list(puru_counts.values()).count(max_count) == 1:
            final_puru = max(puru_counts, key=puru_counts.get)
        else:
            final_puru = None
    else:
        final_puru = None

    letting_go = st.session_state.get("purushartha")

    # ✅ letting_go 제외
    if letting_go and "pada" in df_base.columns:
        df_base = df_base[~df_base["pada"].apply(lambda x: norm_match(x, letting_go))]

    # ✅ final_puru 선택
    if final_puru and "pada" in df_base.columns:
        df_puru = df_base[df_base["pada"].apply(lambda x: norm_match(x, final_puru))]
        if not df_puru.empty:
            df_base = df_puru.copy()

    if df_base.empty:
        st.warning("⚠️ 모든 조건을 통과한 구간이 없습니다.")
        st.stop()

    # ===============================
    # ④ segment 계산
    # ===============================
    df_base = df_base.dropna(subset=["minutes","sign","s_degree","pada"])
    df_base = df_base.sort_values("minutes").reset_index(drop=True)
    df_base["gap"] = df_base["minutes"].diff().fillna(0)
    groups = (df_base["gap"] > 1).cumsum()

    segments = []
    for _, seg in df_base.groupby(groups):
        start_row = seg.iloc[0]
        end_row = seg.iloc[-1]
        start_sign = f"{start_row['sign']} {start_row['s_degree']}"
        end_sign = f"{end_row['sign']} {end_row['s_degree']}"
        segments.append((start_sign, end_sign, start_row.get("nakshatra", "Unknown")))

    # ===============================
    # ⑤ 출력
    # ===============================
    likely_nakshatra = segments[0][2] if segments else "Unknown"

    st.markdown(f"""
    <div class='result-text'>
    <b>likely moon nakshatra:</b><br>
    {likely_nakshatra}<br><br>
    <b>likely sidereal moon range(s):</b><br>
    </div>
    """, unsafe_allow_html=True)

    for s, e, _ in segments:
        st.markdown(f"<div class='result-text'>{s} → {e}</div>", unsafe_allow_html=True)