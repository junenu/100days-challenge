"""Data models for the portfolio site."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SocialLink:
    platform: str
    url: str
    icon: str


@dataclass
class Skill:
    name: str
    level: int  # 0-100
    category: str


@dataclass
class Project:
    title: str
    description: str
    tech: list[str]
    url: Optional[str] = None
    image_emoji: str = "🚀"
    featured: bool = False


@dataclass
class TimelineEntry:
    year: str
    title: str
    organization: str
    description: str
    kind: str = "work"  # "work" | "education"


@dataclass
class Person:
    name: str
    title: str
    tagline: str
    bio: str
    location: str
    email: str
    avatar_initials: str
    skills: list[Skill] = field(default_factory=list)
    projects: list[Project] = field(default_factory=list)
    timeline: list[TimelineEntry] = field(default_factory=list)
    social_links: list[SocialLink] = field(default_factory=list)
