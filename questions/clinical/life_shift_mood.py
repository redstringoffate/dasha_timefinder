# q6_life_shift_mood_en.py

Q6_LIFE_SHIFT_MOOD_CHILD = {
    "id": "life_shift_mood_child",
    "question": (
        "When that change arrived,\n"
        "what color did your inner world take on?"
    ),
    "type": "single_choice",
    "options": [
        {
            "id": "ketu",
            "text": (
                "I spoke less.\n"
                "Often stopped mid-thought.\n"
                "A quiet emptiness opened inside the once-light heart—\n"
                "as if something drifted away from afar.\n"
                "Only a silent breeze remained."
            )
        },
        {
            "id": "venus",
            "text": (
                "I used to find it hard to talk to people,\n"
                "but somehow they began to come closer.\n"
                "I can’t say it was good or bad—it just happened that way."
            )
        },
        {
            "id": "sun",
            "text": (
                "The light days grew a little heavier.\n"
                "I felt eyes turning toward me,\n"
                "and somehow wanted to stand properly.\n"
                "It was as if a quiet light shone on me."
            )
        },
        {
            "id": "moon",
            "text": (
                "The busy noise moved further away.\n"
                "Being alone started to feel natural.\n"
                "The world became a little quieter."
            )
        },
        {
            "id": "mars",
            "text": (
                "It became harder to relax like before.\n"
                "There were sudden moments of tension,\n"
                "and I felt I shouldn’t just stay still—\n"
                "as if I was always getting ready for something."
            )
        },
        {
            "id": "rahu",
            "text": (
                "The time of pure strength had passed,\n"
                "and too many paths opened at once.\n"
                "I couldn’t stay in one place long—\n"
                "new things kept catching my eye.\n"
                "Even in stillness, the wind was moving."
            )
        },
        {
            "id": "jupiter",
            "text": (
                "What was distant began to come closer.\n"
                "Large, slow movements stirred within.\n"
                "It felt like I no longer had to rush—\n"
                "the air itself seemed to whisper, ‘I think I understand.’"
            )
        },
        {
            "id": "saturn",
            "text": (
                "I spoke less.\n"
                "Became cautious for no clear reason.\n"
                "Did the same things again and again.\n"
                "It was a time of long, quiet thinking alone."
            )
        },
        {
            "id": "mercury",
            "text": (
                "Things felt lighter.\n"
                "Small details caught my eye,\n"
                "little joys appeared.\n"
                "My words came a bit faster."
            )
        },
        {
            "id": "unknown",
            "text": (
                "None of these quite fit.\n"
                "I know something changed,\n"
                "but the exact feeling doesn’t come to mind."
            )
        }
    ]
}


Q6_LIFE_SHIFT_MOOD_TEEN = {
    "id": "life_shift_mood_teen",
    "question": (
        "When that change arrived,\n"
        "what color did your inner world take on?"
    ),
    "type": "single_choice",
    "options": [
        {
            "id": "ketu",
            "text": (
                "Things that once made sense stopped making sense.\n"
                "I felt a step away from the world I thought I knew.\n"
                "Confused—but strangely indifferent."
            )
        },
        {
            "id": "venus",
            "text": (
                "The world suddenly looked more complicated.\n"
                "People and feelings drew my curiosity—and my confusion.\n"
                "I wanted to get closer, but quietly watched instead,\n"
                "afraid I might not understand."
            )
        },
        {
            "id": "sun",
            "text": (
                "I thought less about how I felt,\n"
                "and more about who I should become.\n"
                "More than being liked, I wanted to stand firm.\n"
                "I was sensitive—but responsibility had begun to grow."
            )
        },
        {
            "id": "moon",
            "text": (
                "The voice saying ‘be strong’ quieted down,\n"
                "and feelings came forward.\n"
                "The wish to connect with someone grew louder.\n"
                "What I felt started to matter more."
            )
        },
        {
            "id": "mars",
            "text": (
                "I began searching for who I *had* to be,\n"
                "not just who I vaguely was.\n"
                "Action came before thought,\n"
                "and a quiet confidence began to form.\n"
                "The wish to prove myself grew."
            )
        },
        {
            "id": "rahu",
            "text": (
                "My goal had been clear, then the road split into many.\n"
                "Excitement grew—and so did fear.\n"
                "I began to want to go farther than before."
            )
        },
        {
            "id": "jupiter",
            "text": (
                "Scattered thoughts began to find shape.\n"
                "Instead of chasing everything,\n"
                "I wanted to choose one direction.\n"
                "Less possibility—more principle."
            )
        },
        {
            "id": "saturn",
            "text": (
                "I began to see limits and reality\n"
                "where I once saw endless potential.\n"
                "Things I believed easily started to gain weight.\n"
                "For the first time, I felt what effort really meant."
            )
        },
        {
            "id": "mercury",
            "text": (
                "The heaviness lifted a little.\n"
                "Rather than carrying everything alone,\n"
                "I wanted to untangle it through learning and exchange.\n"
                "I started to handle problems with thought, not feeling."
            )
        },
        {
            "id": "unknown",
            "text": (
                "None of these quite fit.\n"
                "I know something changed,\n"
                "but the exact feeling doesn’t come to mind."
            )
        }
    ]
}


def get_shift_mood_question(stage: str):
    if stage == "child":
        return Q6_LIFE_SHIFT_MOOD_CHILD
    elif stage == "teen":
        return Q6_LIFE_SHIFT_MOOD_TEEN
    else:
        raise ValueError("Invalid stage: expected 'child' or 'teen'")
