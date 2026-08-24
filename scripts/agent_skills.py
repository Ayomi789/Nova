from functools import lru_cache
from pathlib import Path
import re


SKILLS_DIR = (
    Path(__file__).resolve().parent.parent
    / ".agents"
    / "skills"
)


SKILL_REGISTRY = {
    "design-taste-frontend": {
        "file": "design-taste-frontend/SKILL.md",
        "label": "design-taste-frontend",
        "keywords": [
            "landing page",
            "landing",
            "portfolio",
            "website",
            "web page",
            "webpage",
            "homepage",
            "home page",
            "hero section",
            "redesign",
            "restyle",
            "make it pretty",
            "make it look",
            "good taste",
            "anti-slop",
        ],
    },
    "image-to-video": {
        "file": "image-to-video/SKILL.md",
        "label": "image-to-video",
        "keywords": [
            "image to video",
            "image-to-video",
            "i2v",
            "animate image",
            "animate this image",
            "animate the image",
            "animate photo",
            "animate this photo",
            "make this move",
            "make it move",
            "into a video",
            "bring it to life",
            "bring this to life",
        ],
    },
    "code-review": {
        "file": "code-review/SKILL.md",
        "label": "code-review",
        "keywords": [
            "code review",
            "review since",
            "review this branch",
            "review the branch",
            "review branch",
            "review this pr",
            "review the pr",
            "review pr",
            "pull request review",
            "review my changes",
            "review the changes",
            "review these changes",
        ],
    },
    "writing-for-agents": {
        "file": "writing-for-agents/SKILL.md",
        "label": "writing-for-agents",
        "keywords": [
            "write a skill",
            "writing a skill",
            "create a skill",
            "creating a skill",
            "new skill for",
            "make a skill",
            "edit the skill",
            "improve the skill",
            "agents.md",
            "claude.md",
        ],
    },
    "customer-research": {
        "file": "customer-research/SKILL.md",
        "label": "customer-research",
        "keywords": [
            "customer research",
            "icp research",
            "talk to customers",
            "analyze transcripts",
            "customer interviews",
            "survey analysis",
            "analyze the survey",
            "support ticket analysis",
            "voice of customer",
            "voc",
            "build personas",
            "customer personas",
            "jobs to be done",
            "jtbd",
            "what do customers say",
            "what do customers want",
            "reddit mining",
            "g2 reviews",
            "review mining",
            "competitor reviews",
            "customer sentiment",
            "why customers churn",
            "customer churn",
            "forum research",
            "community research",
        ],
    },
    "css-animations": {
        "file": "css-animations/SKILL.md",
        "label": "css-animations",
        "keywords": [
            "css animation",
            "css animations",
            "css transition",
            "keyframes",
            "hover effect",
            "scroll animation",
            "animate on scroll",
            "scroll-driven",
            "micro-interaction",
            "page transition",
            "skeleton shimmer",
            "loading shimmer",
            "fade in on scroll",
        ],
    },
    "motion-graphics": {
        "file": "motion-graphics/SKILL.md",
        "label": "motion-graphics",
        "keywords": [
            "motion graphics",
            "motion design",
            "kinetic typography",
            "logo sting",
            "lower third",
            "explainer video",
            "animated map",
            "count up animation",
            "stat count-up",
        ],
    },
    "hyperframes-animation": {
        "file": "hyperframes-animation/SKILL.md",
        "label": "hyperframes-animation",
        "keywords": [
            "hyperframes",
            "gsap timeline",
            "lottie animation",
            "anime.js",
            "scene transition video",
        ],
    },
    "canvas-design": {
        "file": "canvas-design/SKILL.md",
        "label": "canvas-design",
        "keywords": [
            "poster",
            "make a poster",
            "design a poster",
            "create art",
            "piece of art",
            "visual art",
            "artwork for",
            "event flyer",
            "album cover",
            "book cover",
        ],
    },
    "improve-codebase-architecture": {
        "file": "improve-codebase-architecture/SKILL.md",
        "label": "improve-codebase-architecture",
        "keywords": [
            "improve the architecture",
            "improve codebase architecture",
            "codebase architecture",
            "architecture review",
            "architectural review",
            "architecture opportunities",
            "deepening opportunities",
            "shallow modules",
        ],
    },
    "firebase-security-rules-auditor": {
        "file": "firebase-security-rules-auditor/SKILL.md",
        "label": "firebase-security-rules-auditor",
        "keywords": [
            "firebase rules",
            "firestore rules",
            "security rules",
            "storage rules",
            "audit firestore",
            "audit my rules",
            "rules audit",
            "red-team rules",
        ],
    },
}


def _matches(keyword, clean):
    if " " in keyword or len(keyword) >= 4:
        return keyword in clean

    return re.search(rf"\b{re.escape(keyword)}\b", clean) is not None


@lru_cache(maxsize=None)
def _load_skill(rel_path):
    """
    Load one installed skill file once.
    Returns an empty string when missing.
    """

    path = SKILLS_DIR / rel_path

    if not path.exists():
        return ""

    try:
        return path.read_text(
            encoding="utf-8",
        )

    except Exception:
        return ""


def collect_skills(prompt):
    """
    Return [(label, content)] for every registered
    skill whose keywords match the prompt.
    """

    if not prompt:
        return []

    clean = prompt.strip().lower()

    out = []

    for spec in SKILL_REGISTRY.values():

        hit = any(
            _matches(keyword, clean)
            for keyword in spec["keywords"]
        )

        if not hit:
            continue

        content = _load_skill(spec["file"])

        if content:
            out.append((spec["label"], content))

    return out
