# q5_life_shift_en.py

Q5_LIFE_SHIFT = {
    "id": "life_shift_timing",
    "type": "single_choice",
    "question": (
        "Was there a moment when the ‘atmosphere of the world’ seemed to change for you?\n"
        "It doesn’t have to be from childhood.\n"
        "For some, it comes around early school years;\n"
        "for others, during adolescence or early adulthood.\n"
        "Choose the period that feels closest to when that shift occurred."
    ),
    "options": [
        {
            "id": "child",
            "text": (
                "The air suddenly changed when I still knew little about the world. (early childhood)"
            ),
            "condition": "pre_puberty"
        },
        {
            "id": "puberty_start",
            "text": (
                "It was when friendships and the rules of the world began to grow complicated. (late elementary to early adolescence)"
            ),
            "condition": "puberty_start"
        },
        {
            "id": "puberty",
            "text": (
                "It was the time when conflicts arose within me, and I began to wrestle with myself. (adolescence)"
            ),
            "condition": "puberty"
        },
        {
            "id": "post_puberty",
            "text": (
                "It came around the time I was about to become an adult—when responsibility and choice began to fall on me. (late teens to early adulthood)"
            ),
            "condition": "post_puberty"
        },
        {
            "id": "20s",
            "text": (
                "When I stepped into society, and the world began to press its real weight upon me. (early to mid-twenties)"
            ),
            "condition": "early_20s_only"
        },
        {
            "id": "no_shift",
            "text": (
                "I haven’t really felt such a moment—or can’t recall one clearly."
            ),
            "condition": "no_shift_option"
        },
        {
            "id": "turmoil",
            "text": (
                "My life has always been full of upheaval; it’s hard to say one moment stood out more than the rest."
            ),
            "condition": "always"
        }
    ]
}
