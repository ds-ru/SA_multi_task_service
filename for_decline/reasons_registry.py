from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class DeclineReason:
    """
    Ad decline reason.
    Domain model, not tied to DB or Telegram API.
    """
    id: int
    title: str
    description_html: str


class DeclineReasonsRegistry:
    """
    Registry of all available decline reasons.
    Single source of truth.
    """
    # порядок по популярности (на основе статистики)
    _popular_order = [
        2,  # Editorial requirements
        18,  # Prohibited content
        31,  # Destination quality
        33,  # Irrelevant destinations
        32,  # Destination functionality
        23,  # Politics, sensitive, religion
    ]

    _reasons: Dict[int, DeclineReason] = {
        1: DeclineReason(
            id=1,
            title="Ad format",
            description_html=(
                "Ads can only promote products inside Telegram, such as channels or bots."
            ),
        ),
        2: DeclineReason(
            id=2,
            title="Editorial requirements",
            description_html=(
                "Standard requirements of style, clarity, spelling, and punctuation apply to all ads. "
                "Numbers, symbols, and formatting must be used properly. "
                "https://promote.telegram.org/guidelines#2-editorial-requirements"
                "Read more about this issue"
            ),
        ),
        3: DeclineReason(
            id=3,
            title="Link format",
            description_html=(
                "The ad link and the link in the ad text must both lead to the same Telegram channel or bot. "
                "Only one link is allowed in the ad text (in the format @link or t.me/link). "
                "https://promote.telegram.org/guidelines#3-link-format"
                "Read more about this issue"
            ),
        ),
        4: DeclineReason(
            id=4,
            title="Destination",
            description_html=(
                "The destination Telegram channel or bot must be technically and visually complete, "
                "fully functional, and consistent with the ad content. "
                "Destination channels must be public. "
                "https://promote.telegram.org/guidelines#4-destination"
                "Read more about this issue"
            ),
        ),
        18: DeclineReason(
            id=18,
            title="Prohibited content",
            description_html=(
                "These Ad Policies prohibit certain types of content to ensure a safe and pleasant "
                "experience for Telegram users. "
                "https://promote.telegram.org/guidelines#5-prohibited-content"
                "Read more about this issue"
            ),
        ),
        19: DeclineReason(
            id=19,
            title="Graphic, shocking, or sexual content",
            description_html=(
                "Ads must not promote graphic, shocking, or sexual content, products, or services. "
                "https://promote.telegram.org/guidelines#5-1-graphic-shocking-or-sexual-content"
                "Read more about this issue"
            ),
        ),
        20: DeclineReason(
            id=20,
            title="Hate, violence, harassment",
            description_html=(
                "Ads must not promote hatred, intolerance, harassment, discrimination, violence, or abuse. "
                "https://promote.telegram.org/guidelines#5-2-hate-violence-harassment"
                "Read more about this issue"
            ),
        ),
        21: DeclineReason(
            id=21,
            title="Third party rights",
            description_html=(
                "Ads must not promote or violate third-party rights, including trademark, copyright, "
                "privacy, or other personal or proprietary rights. "
                "https://promote.telegram.org/guidelines#5-3-third-party-rights"
                "Read more about this issue"
            ),
        ),
        22: DeclineReason(
            id=22,
            title="Deceptive, misleading, or predatory advertising",
            description_html=(
                "Ads must not contain false or misleading content, or content that does not match "
                "the promoted product. This includes false claims, promises, or predatory practices. "
                "https://promote.telegram.org/guidelines#5-4-deceptive-misleading-or-predatory-advertising"
                "Read more about this issue"
            ),
        ),
        23: DeclineReason(
            id=23,
            title="Politics, sensitive topics, religion",
            description_html=(
                "Ads must not promote political campaigns, elections, political parties, candidates, "
                "or political or religious movements. "
                "https://promote.telegram.org/guidelines#5-5-elections-political-ads-religion"
                "Read more about this issue"
            ),
        ),
        24: DeclineReason(
            id=24,
            title="Gambling",
            description_html=(
                "Ads must not promote online or offline gambling, gaming, or casino activities "
                "involving real money, prizes, or items of value. "
                "https://promote.telegram.org/guidelines#5-6-gambling"
                "Read more about this issue"
            ),
        ),
        25: DeclineReason(
            id=25,
            title="Deceptive or harmful financial products or services",
            description_html=(
                "Ads must not promote content, products, or services associated with deceptive "
                "or harmful financial practices. "
                "https://promote.telegram.org/guidelines#5-7-deceptive-or-harmful-financial-products-or-services"
                "Read more about this issue"
            ),
        ),
        26: DeclineReason(
            id=26,
            title="Medical services, medications, supplements",
            description_html=(
                "Ads must not promote content, products, or services related to health, medicine, "
                "or wellness. "
                "https://promote.telegram.org/guidelines#5-8-uncertified-medical-services-medications-supplements"
                "Read more about this issue"
            ),
        ),
        27: DeclineReason(
            id=27,
            title="Drugs, alcohol, tobacco",
            description_html=(
                "Ads must not promote psychoactive substances, alcoholic beverages, or tobacco products. "
                "https://promote.telegram.org/guidelines#5-9-drugs-alcohol-tobacco-fast-food"
                "Read more about this issue"
            ),
        ),
        28: DeclineReason(
            id=28,
            title="Weapons, firearms, explosives, ammunition",
            description_html=(
                "Ads must not promote the sale of weapons, firearms, explosives, ammunition, "
                "or related content. "
                "https://promote.telegram.org/guidelines#5-10-weapons-firearms-explosives-ammunition"
                "Read more about this issue"
            ),
        ),
        29: DeclineReason(
            id=29,
            title="Spam software, malware, hacking",
            description_html=(
                "Ads must not promote spam, malware, hacking tools, or services intended to gain "
                "unauthorized access to user devices or cause harm. "
                "https://promote.telegram.org/guidelines#5-11-spam-software-malware-hacking"
                "Read more about this issue"
            ),
        ),
        30: DeclineReason(
            id=30,
            title="Products of questionable legality",
            description_html=(
                "Ads must not promote content, products, or services of questionable or unclear legality. "
                "https://promote.telegram.org/guidelines#5-12-products-of-questionable-legality"
                "Read more about this issue"
            ),
        ),
        31: DeclineReason(
            id=31,
            title="Destination quality",
            description_html=(
                "Ad destinations must provide original, high-quality content and a proper user experience. "
                "https://promote.telegram.org/guidelines#4-1-destination-quality"
                "Read more about this issue"
            ),
        ),
        32: DeclineReason(
            id=32,
            title="Destination functionality",
            description_html=(
                "Ad destinations must be functional, technically complete, and actively maintained. "
                "https://promote.telegram.org/guidelines#4-2-destination-functionality"
                "Read more about this issue"
            ),
        ),
        33: DeclineReason(
            id=33,
            title="Irrelevant destinations",
            description_html=(
                "The language of the ad and its destination must match the language of the targeted channel. "
                "https://promote.telegram.org/guidelines#4-3-irrelevant-destinations"
                "Read more about this issue"
            ),
        ),
        34: DeclineReason(
            id=34,
            title="Manipulation of content",
            description_html=(
                "Destination content must not be altered to deceive users or evade moderation. "
                "https://promote.telegram.org/guidelines#4-4-manipulation-of-content"
                "Read more about this issue"
            ),
        ),
        35: DeclineReason(
            id=35,
            title="Contract terms",
            description_html=(
                "This ad has been suspended in accordance with the applicable advertising agreement."
            ),
        ),
    }

    @classmethod
    def get(cls, reason_id: int) -> DeclineReason:
        if reason_id not in cls._reasons:
            raise ValueError(f"Unknown decline reason id: {reason_id}")
        return cls._reasons[reason_id]

    @classmethod
    def all(cls) -> List[DeclineReason]:
        ordered = []

        # сначала популярные
        for rid in cls._popular_order:
            if rid in cls._reasons:
                ordered.append(cls._reasons[rid])

        # затем остальные (стабильно, по id)
        for rid in sorted(cls._reasons.keys()):
            if rid not in cls._popular_order:
                ordered.append(cls._reasons[rid])

        return ordered

