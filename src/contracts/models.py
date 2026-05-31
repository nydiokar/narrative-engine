from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# ── Enums (from types_maps.md and research/) ──────────────────────────────

class PremiseType(str, Enum):
    QUEST = "quest"
    ESCAPE = "escape"
    REVENGE = "revenge"
    DISCOVERY = "discovery"
    TRANSFORMATION = "transformation"
    SURVIVAL = "survival"
    MYSTERY = "mystery"
    FORBIDDEN_DESIRE = "forbidden_desire"
    FALL_FROM_GRACE = "fall_from_grace"
    RISE_TO_POWER = "rise_to_power"
    REDEMPTION = "redemption"
    CORRUPTION = "corruption"
    COMING_OF_AGE = "coming_of_age"
    CONSPIRACY = "conspiracy"
    INVASION = "invasion"
    RESCUE = "rescue"
    RETURN_HOME = "return_home"
    DOUBLE_LIFE = "double_life"
    HIDDEN_IDENTITY = "hidden_identity"
    IMPOSSIBLE_CHOICE = "impossible_choice"
    MORAL_TEST = "moral_test"
    SOCIAL_ASCENT = "social_ascent"
    SOCIAL_EXILE = "social_exile"
    MONSTER_CONFRONTATION = "monster_confrontation"
    WORLD_RESTORATION = "world_restoration"
    TRUTH_REVELATION = "truth_revelation"
    INHERITANCE = "inheritance"
    SACRIFICE = "sacrifice"
    REBELLION = "rebellion"
    CURSED_FATE = "cursed_fate"


class EndingType(str, Enum):
    RESTORATION = "restoration"
    TRANSFORMATION = "transformation"
    TRAGIC = "tragic"
    BITTERSWEET = "bittersweet"
    PYRRHIC_VICTORY = "pyrrhic_victory"
    AMBIGUOUS = "ambiguous"
    CIRCULAR = "circular"
    OPEN = "open"
    REVELATORY = "revelatory"
    IRONIC = "ironic"
    REDEMPTIVE = "redemptive"
    CORRUPTION = "corruption"
    SACRIFICIAL = "sacrificial"
    FALSE_HAPPY = "false_happy"
    COSMIC_HORROR = "cosmic_horror"
    ROMANTIC_UNION = "romantic_union"
    ROMANTIC_SEPARATION = "romantic_separation"
    COMING_HOME = "coming_home"
    EXILE = "exile"
    ASCENSION = "ascension"
    FALL = "fall"


class SceneType(str, Enum):
    INTRODUCTION = "introduction"
    INCITING = "inciting"
    DECISION = "decision"
    DISCOVERY = "discovery"
    CONFRONTATION = "confrontation"
    INTERROGATION = "interrogation"
    SEDUCTION = "seduction"
    BETRAYAL = "betrayal"
    REVERSAL = "reversal"
    REVELATION = "revelation"
    TRAINING = "training"
    TEST = "test"
    NEGOTIATION = "negotiation"
    ESCAPE = "escape"
    CHASE = "chase"
    BATTLE = "battle"
    QUIET_AFTERMATH = "quiet_aftermath"
    RECOGNITION = "recognition"
    JUDGMENT = "judgment"
    SACRIFICE = "sacrifice"
    TEMPTATION = "temptation"
    FALSE_VICTORY = "false_victory"
    DARK_NIGHT = "dark_night"
    CLIMAX = "climax"
    RESOLUTION = "resolution"
    EPILOGUE = "epilogue"


class SequenceType(str, Enum):
    QUEST = "quest"
    INVESTIGATION = "investigation"
    TRAINING = "training"
    PURSUIT = "pursuit"
    INFILTRATION = "infiltration"
    COURTSHIP = "courtship"
    TRIAL = "trial"
    BATTLE = "battle"
    ESCAPE = "escape"
    DESCENT = "descent"
    REVELATION = "revelation"
    TRANSFORMATION = "transformation"
    BETRAYAL = "betrayal"
    RECONCILIATION = "reconciliation"
    CORRUPTION = "corruption"
    REDEMPTION = "redemption"
    RETURN = "return"


class StakesType(str, Enum):
    LIFE_DEATH = "life_death"
    FREEDOM_CAPTIVITY = "freedom_captivity"
    LOVE_LOSS = "love_loss"
    TRUTH_IGNORANCE = "truth_ignorance"
    HONOR_SHAME = "honor_shame"
    BELONGING_EXILE = "belonging_exile"
    POWER_SUBJUGATION = "power_subjugation"
    IDENTITY_ERASURE = "identity_erasure"
    MEMORY_OBLIVION = "memory_oblivion"
    ORDER_CHAOS = "order_chaos"
    JUSTICE_CORRUPTION = "justice_corruption"
    SURVIVAL_EXTINCTION = "survival_extinction"
    FAMILY_SEPARATION = "family_separation"
    COMMUNITY_COLLAPSE = "community_collapse"
    SOUL_DAMNATION = "soul_damnation"
    LEGACY_MEANINGLESSNESS = "legacy_meaninglessness"
    FUTURE_STAGNATION = "future_stagnation"
    INNOCENCE_CORRUPTION = "innocence_corruption"
    RECOGNITION_INVISIBILITY = "recognition_invisibility"
    AUTONOMY_CONTROL = "autonomy_control"


class CanonicalPhase(str, Enum):
    MANIPULATION = "manipulation"
    COMPETENCE = "competence"
    PERFORMANCE = "performance"
    SANCTION = "sanction"


class ModalityType(str, Enum):
    WANTING = "wanting"
    KNOWING = "knowing"
    BEING_ABLE = "being_able"
    HAVING_TO = "having_to"


class ModalityState(str, Enum):
    # wanting
    DESIRES = "desires"
    INDIFFERENT = "indifferent"
    REJECTS = "rejects"
    # knowing
    KNOWS = "knows"
    PARTIALLY_KNOWS = "partially_knows"
    IGNORANT = "ignorant"
    # being_able
    ABLE = "able"
    UNABLE = "unable"
    # having_to
    OBLIGATED = "obligated"
    FREE = "free"


class ConflictType(str, Enum):
    INTERNAL = "internal"
    INTERPERSONAL = "interpersonal"
    INSTITUTIONAL = "institutional"
    ENVIRONMENTAL = "environmental"
    EPISTEMIC = "epistemic"
    METAPHYSICAL = "metaphysical"
    SYSTEMIC = "systemic"


class ClassicalConflictType(str, Enum):
    PERSON_VS_PERSON = "person_vs_person"
    PERSON_VS_SELF = "person_vs_self"
    PERSON_VS_SOCIETY = "person_vs_society"
    PERSON_VS_NATURE = "person_vs_nature"
    PERSON_VS_FATE = "person_vs_fate"
    PERSON_VS_TECHNOLOGY = "person_vs_technology"
    PERSON_VS_SUPERNATURAL = "person_vs_supernatural"
    PERSON_VS_GOD = "person_vs_god"
    PERSON_VS_INSTITUTION = "person_vs_institution"
    PERSON_VS_MEMORY = "person_vs_memory"
    PERSON_VS_TIME = "person_vs_time"
    PERSON_VS_DESIRE = "person_vs_desire"


class ConflictOperation(str, Enum):
    BLOCK = "block"
    DELAY = "delay"
    STEAL = "steal"
    HIDE = "hide"
    CORRUPT = "corrupt"
    COUNTERFEIT = "counterfeit"
    TEMPT = "tempt"
    DECEIVE = "deceive"
    FORBID = "forbid"
    PUNISH = "punish"
    MISRECOGNIZE = "misrecognize"
    DISPLACE = "displace"
    INVERT = "invert"
    TRAP = "trap"
    EXPLOIT = "exploit"
    REVEAL = "reveal"
    TRANSFER = "transfer"
    SACRIFICE = "sacrifice"
    DESTROY = "destroy"
    TRANSFORM = "transform"


class ConflictQualityLevel(str, Enum):
    WEAK = "weak"
    GOOD = "good"
    STRONG = "strong"
    GREAT = "great"
    TRAGIC = "tragic"
    MYTHIC = "mythic"


class Intensity(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class JunctionType(str, Enum):
    CONJUNCTION = "conjunction"
    DISJUNCTION = "disjunction"


class ValueState(str, Enum):
    LOVE = "love"
    RECOGNITION = "recognition"
    FREEDOM = "freedom"
    TRUTH = "truth"
    REVENGE = "revenge"
    BELONGING = "belonging"
    LEGITIMACY = "legitimacy"
    INHERITANCE = "inheritance"
    FORGIVENESS = "forgiveness"
    CONTROL = "control"
    RESTORATION_OF_ORDER = "restoration_of_order"
    ESCAPE_FROM_SHAME = "escape_from_shame"
    JUSTICE = "justice"
    POWER = "power"
    IDENTITY = "identity"
    SURVIVAL = "survival"
    HONOR = "honor"
    MEMORY = "memory"
    MEANING = "meaning"
    INNOCENCE = "innocence"


class PlutchikEmotion(str, Enum):
    JOY = "joy"
    TRUST = "trust"
    FEAR = "fear"
    SURPRISE = "surprise"
    SADNESS = "sadness"
    DISGUST = "disgust"
    ANGER = "anger"
    ANTICIPATION = "anticipation"


class FFMScore(int, Enum):
    """Five-Factor Model trait score 1-10."""

    MIN = 1
    MAX = 10


class AudienceBand(str, Enum):
    MIDDLE_GRADE = "middle_grade"
    YOUNG_ADULT = "young_adult"
    ADULT = "adult"


class SeriesType(str, Enum):
    STANDALONE = "standalone"
    DUOLOGY = "duology"
    TRILOGY = "trilogy"
    SERIES = "series"


class GoalPolarity(str, Enum):
    ATTAIN = "attain"
    MAINTAIN = "maintain"
    LEAVE = "leave"
    AVOID = "avoid"


class AttachmentPattern(str, Enum):
    SECURE = "secure"
    ANXIOUS_PREOCCUPIED = "anxious_preoccupied"
    DISMISSIVE_AVOIDANT = "dismissive_avoidant"
    FEARFUL_AVOIDANT = "fearful_avoidant"


class RelationalModel(str, Enum):
    COMMUNAL_SHARING = "communal_sharing"
    AUTHORITY_RANKING = "authority_ranking"
    EQUALITY_MATCHING = "equality_matching"
    MARKET_PRICING = "market_pricing"


class POV(str, Enum):
    FIRST_PERSON = "first_person"
    SECOND_PERSON = "second_person"
    THIRD_LIMITED = "third_limited"
    THIRD_OMNISCIENT = "third_omniscient"
    THIRD_OBJECTIVE = "third_objective"


class Tense(str, Enum):
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"


class StoryStatus(str, Enum):
    SEED = "seed"
    BRIEF = "brief"
    BIBLE = "bible"
    OUTLINE = "outline"
    DRAFT = "draft"
    DEVELOPMENTAL = "developmental"
    LINE = "line"
    COPY = "copy"
    PROOF = "proof"
    FINAL = "final"


# ── Value Objects ─────────────────────────────────────────────────────────

class ModalitySet(BaseModel):
    wanting: ModalityState = ModalityState.INDIFFERENT
    knowing: ModalityState = ModalityState.IGNORANT
    being_able: ModalityState = ModalityState.UNABLE
    having_to: ModalityState = ModalityState.FREE


class ConflictLoad(BaseModel):
    internal: Intensity = Intensity.NONE
    interpersonal: Intensity = Intensity.NONE
    institutional: Intensity = Intensity.NONE
    environmental: Intensity = Intensity.NONE
    epistemic: Intensity = Intensity.NONE
    metaphysical: Intensity = Intensity.NONE
    systemic: Intensity = Intensity.NONE


class CharacterEmotionalState(BaseModel):
    emotion: PlutchikEmotion
    intensity: Intensity


# ── Contracts ─────────────────────────────────────────────────────────────

class BriefLayer(BaseModel):
    medium: str = "novel"
    audience_band: AudienceBand
    language: str = "en"
    target_word_count: int = 50000
    series_type: SeriesType = SeriesType.STANDALONE
    content_limits: list[str] = Field(default_factory=list)


class Comp(BaseModel):
    title: str
    author: str
    similarity_reason: str = ""


class ConceptLayer(BaseModel):
    story_promise: str = ""
    comps: list[Comp] = Field(default_factory=list)


class GenreSelection(BaseModel):
    primary_bisac: str = ""
    secondary_bisac: list[str] = Field(default_factory=list)
    subgenre_notes: str = ""


class NarrativeProgramPhase(BaseModel):
    manipulation: bool = False
    competence: bool = False
    performance: bool = False
    sanction: bool = False


class NarrativeProgramRef(BaseModel):
    id: UUID
    subject: str
    object_of_value: ValueState
    canonical_phases_completed: NarrativeProgramPhase = Field(default_factory=NarrativeProgramPhase)


class FabulaChain(BaseModel):
    events: list[UUID] = Field(default_factory=list)
    causality_chains: list[str] = Field(default_factory=list)


class StoryContract(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    premise: str
    premise_type: PremiseType | None = None
    ending_type: EndingType | None = None
    logline: str = ""
    hook: str = ""

    brief_layer: BriefLayer | None = None
    concept_layer: ConceptLayer = Field(default_factory=ConceptLayer)
    genre: GenreSelection = Field(default_factory=GenreSelection)
    theme_contract_id: UUID | None = None

    # Actantial model
    subject_id: str = ""
    object_of_value_id: str = ""
    object_of_value_type: ValueState | None = None
    object_of_value_description: str = ""
    sender_id: str = ""
    receiver_id: str = ""
    helper_ids: list[str] = Field(default_factory=list)
    opponent_ids: list[str] = Field(default_factory=list)

    narrative_programs: list[NarrativeProgramRef] = Field(default_factory=list)
    conflict_contract_id: UUID | None = None
    discourse_contract_id: UUID | None = None

    fabula: FabulaChain = Field(default_factory=FabulaChain)
    episodes: list[UUID] = Field(default_factory=list)
    chapters: list[UUID] = Field(default_factory=list)

    status: StoryStatus = StoryStatus.SEED


class CharacterValues(BaseModel):
    primary: str = ""
    secondary: list[str] = Field(default_factory=list)
    priorities: dict[str, int] = Field(default_factory=dict)


class PersonalityProfile(BaseModel):
    openness: int = Field(default=5, ge=1, le=10)
    conscientiousness: int = Field(default=5, ge=1, le=10)
    extraversion: int = Field(default=5, ge=1, le=10)
    agreeableness: int = Field(default=5, ge=1, le=10)
    neuroticism: int = Field(default=5, ge=1, le=10)


class CharacterArc(BaseModel):
    initial_state: str = ""
    terminal_state: str = ""
    personality_changes: list[dict] = Field(default_factory=list)
    value_shifts: list[dict] = Field(default_factory=list)


class Relationship(BaseModel):
    target_id: str
    relation: str
    relational_model: RelationalModel | None = None
    tension: Intensity = Intensity.NONE


class CharacterContract(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str = ""

    # Layer 1: Function
    actant_roles: list[str] = Field(default_factory=list)

    # Layer 2: Personality
    personality: PersonalityProfile = Field(default_factory=PersonalityProfile)

    # Layer 3: Values
    values: CharacterValues = Field(default_factory=CharacterValues)

    # Layer 4: Social Mode
    social_mode_default: RelationalModel | None = None

    # Layer 5: Attachment
    attachment_pattern: AttachmentPattern | None = None

    # Motivation stack
    core_desires: list[str] = Field(default_factory=list)
    core_fears: list[str] = Field(default_factory=list)
    wound_types: list[str] = Field(default_factory=list)
    need_types: list[str] = Field(default_factory=list)
    goal_polarity: GoalPolarity = GoalPolarity.ATTAIN

    # Modalities (Greimas)
    modalities: ModalitySet = Field(default_factory=ModalitySet)

    # Emotional baseline
    emotional_baseline_emotion: PlutchikEmotion | None = None
    emotional_baseline_intensity: Intensity = Intensity.LOW

    arc: CharacterArc = Field(default_factory=CharacterArc)
    relationships: list[Relationship] = Field(default_factory=list)


class ObjectOfValueContract(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    type: ValueState
    description: str = ""
    domain: str = "personal"
    polarity: str = "positive"
    current_possessor: str = ""
    desired_by: list[str] = Field(default_factory=list)
    significance: str = ""


class EpistemicState(BaseModel):
    """Tracks what each character knows, preventing Deus ex machina."""

    character_id: UUID
    known_facts: list[str] = Field(default_factory=list)
    unknown_facts: list[str] = Field(default_factory=list)
    misbeliefs: list[tuple[str, str]] = Field(default_factory=list)


class GreimasEpisodeTracking(BaseModel):
    subject: str = ""
    object_of_value: str = ""
    current_state: str = ""
    desired_transformation: str = ""
    opponent: str = ""
    opponent_value_logic: str = ""
    helper: str = ""
    modality_gained: str = ""
    modality_lost: str = ""
    action_type: str = ""
    resulting_state: str = ""
    sanction_or_judgment: str = ""
    contribution_to_whole_fabula: str = ""


class EpisodeContract(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str = ""
    sequence_number: int = 0
    summary: str = ""

    sequence_type: SequenceType | None = None
    stakes_type: StakesType | None = None

    greimas_tracking: GreimasEpisodeTracking = Field(default_factory=GreimasEpisodeTracking)
    canonical_phase: CanonicalPhase = CanonicalPhase.MANIPULATION
    narrative_programs: list[UUID] = Field(default_factory=list)
    propp_functions: list[str] = Field(default_factory=list)

    themes_active: list[UUID] = Field(default_factory=list)
    dominant_conflict: ConflictType = ConflictType.INTERPERSONAL
    chapters: list[UUID] = Field(default_factory=list)

    modality_shifts: list[dict] = Field(default_factory=list)
    emotional_arc_opening: PlutchikEmotion | None = None
    emotional_arc_closing: PlutchikEmotion | None = None

    status: str = "draft"


class GreimasSceneDiagnostic(BaseModel):
    state_before: str = ""
    action_occurs: str = ""
    state_after: str = ""
    value_object_change: str = "none"
    future_action_possible_or_blocked: str = ""
    diagnostic_pass: bool = False


class SceneContract(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    episode_id: UUID | None = None
    chapter_id: UUID | None = None
    sequence_number: int = 0

    scene_type: SceneType | None = None

    setting_location: str = ""
    setting_time: str = ""
    setting_atmosphere: str = ""

    characters_present: list[dict] = Field(default_factory=list)

    greimas_diagnostic: GreimasSceneDiagnostic = Field(default_factory=GreimasSceneDiagnostic)

    events: list[UUID] = Field(default_factory=list)
    propp_function: str = ""
    canonical_phase: CanonicalPhase = CanonicalPhase.MANIPULATION
    narrative_program_advanced: UUID | None = None

    conflict_load: ConflictLoad = Field(default_factory=ConflictLoad)
    modality_changes: list[dict] = Field(default_factory=list)
    emotional_tone: PlutchikEmotion | None = None

    content: str = ""
    word_count: int = 0
    status: str = "draft"


class ChapterContract(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    episode_id: UUID | None = None
    sequence_number: int = 0
    title: str = ""
    summary: str = ""
    narrative_programs_active: list[UUID] = Field(default_factory=list)
    scenes: list[UUID] = Field(default_factory=list)
    chapter_arc_opening: str = ""
    chapter_arc_closing: str = ""
    primary_conflict_type: ConflictType = ConflictType.INTERPERSONAL
    word_count_target: int = 0
    status: str = "outline"


class ThemeContract(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    primary_themes: list[dict] = Field(default_factory=list)
    secondary_themes: list[dict] = Field(default_factory=list)
    moral_tensions: list[dict] = Field(default_factory=list)
    symbolic_motifs: list[dict] = Field(default_factory=list)
    theme_progression: list[dict] = Field(default_factory=list)


class GlobalConflict(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: ConflictType
    classical_type: ClassicalConflictType | None = None
    operations: list[ConflictOperation] = Field(default_factory=list)
    quality_level: ConflictQualityLevel = ConflictQualityLevel.GOOD
    description: str = ""
    primary_actants: list[str] = Field(default_factory=list)
    object_of_value: str = ""
    intensity: Intensity = Intensity.MEDIUM
    resolution_criteria: str = ""


class SceneConflictLoad(BaseModel):
    scene_id: UUID
    conflict_load: ConflictLoad = Field(default_factory=ConflictLoad)
    dominant_type: ConflictType = ConflictType.INTERPERSONAL


class ConflictContract(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    global_conflicts: list[GlobalConflict] = Field(default_factory=list)
    per_scene_conflict_load: list[SceneConflictLoad] = Field(default_factory=list)


class DiscourseContract(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    story_id: UUID | None = None
    point_of_view: POV = POV.THIRD_LIMITED
    tense: Tense = Tense.PAST
    voice_register: str = "neutral"
    temporal_handling: str = "chronological"
    exposition_strategy: str = "integrated"
    suspense_strategy: str = "suspense"
    discourse_events: list[dict] = Field(default_factory=list)


class CritiqueDimensionScore(BaseModel):
    value: int = Field(default=0, ge=0, le=10)
    issues: list[str] = Field(default_factory=list)


class FabulaCoherenceCheck(BaseModel):
    check: str
    pass_: bool = Field(default=False, alias="pass")
    violations: list[str] = Field(default_factory=list)


class CritiqueContract(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    target_id: UUID | None = None
    target_type: str = ""
    reviewer: str = "critic"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    greimas_checks: list[FabulaCoherenceCheck] = Field(default_factory=list)

    coherence: CritiqueDimensionScore = Field(default_factory=CritiqueDimensionScore)
    completeness: CritiqueDimensionScore = Field(default_factory=CritiqueDimensionScore)
    character_consistency: CritiqueDimensionScore = Field(default_factory=CritiqueDimensionScore)
    no_filler_compliance: CritiqueDimensionScore = Field(default_factory=CritiqueDimensionScore)
    structural_fidelity: CritiqueDimensionScore = Field(default_factory=CritiqueDimensionScore)

    verdict: str = "fail"
    summary: str = ""
    revision_actions: list[dict] = Field(default_factory=list)
