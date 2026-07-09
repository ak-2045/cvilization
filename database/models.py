from pydantic import BaseModel, Field
from typing import List, Optional

class PersonalInfoModel(BaseModel):
    id: Optional[int] = None
    name: str = ""
    phone: str = ""
    email: str = ""
    college_email: str = ""
    github: str = ""
    github_link: str = ""
    linkedin: str = ""
    linkedin_link: str = ""
    portfolio: str = ""
    location: str = ""
    degree: str = ""
    branch: str = ""
    college: str = ""
    graduation_year: str = ""
    cgpa: str = ""
    roll_number: str = ""
    profile_photo: str = ""

class EducationModel(BaseModel):
    id: Optional[int] = None
    degree: str
    institute: str
    board_university: str
    cgpa_percentage: str
    year: str
    is_selected: bool = True
    sort_order: int = 0

class ExperienceModel(BaseModel):
    id: Optional[int] = None
    role: str
    company: str
    location: str
    dates: str
    technologies: List[str] = Field(default_factory=list)
    bullets: List[str] = Field(default_factory=list)
    is_selected: bool = True
    sort_order: int = 0

class ProjectModel(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    tech_stack: List[str] = Field(default_factory=list)
    github_link: str = ""
    live_demo_link: str = ""
    duration: str = ""
    bullets: List[str] = Field(default_factory=list)
    is_selected: bool = True
    sort_order: int = 0

class SkillModel(BaseModel):
    id: Optional[int] = None
    category: str
    items: List[str] = Field(default_factory=list)
    is_selected: bool = True
    sort_order: int = 0

class CertificationModel(BaseModel):
    id: Optional[int] = None
    name: str
    date: str
    issuer: str
    credential_url: str = ""
    is_selected: bool = True
    sort_order: int = 0

class AchievementModel(BaseModel):
    id: Optional[int] = None
    category: str
    description: str
    is_selected: bool = True
    sort_order: int = 0

class JobDescriptionModel(BaseModel):
    id: Optional[int] = None
    title: str = ""
    raw_text: str = ""
    analysis_json: Optional[str] = None

class FullResumeModel(BaseModel):
    personal_info: PersonalInfoModel
    education: List[EducationModel] = Field(default_factory=list)
    experiences: List[ExperienceModel] = Field(default_factory=list)
    projects: List[ProjectModel] = Field(default_factory=list)
    skills: List[SkillModel] = Field(default_factory=list)
    certifications: List[CertificationModel] = Field(default_factory=list)
    achievements: List[AchievementModel] = Field(default_factory=list)
