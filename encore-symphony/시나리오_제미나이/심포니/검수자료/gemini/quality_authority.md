# Korean translation quality

## Scope, authority, and precedence

This is the authoritative shared semantic-quality standard for translating, retranslating, or editing Japanese visual novels and dialogue-heavy games into Korean. Read it **before writing the first semantic draft**, not only during review.

The default decision unit is:

`Japanese source + scene context + speaker + addressee + relationship + story phase -> natural Korean`

Do not reduce the task to `Japanese sentence -> Korean sentence`.

Engine-specific skills and project style guides may add work-specific names, terminology, voice notes, structural constraints, or an explicitly requested artistic exception. They may not weaken this document's first-pass quality, spoken-naturalness, directed-relationship voice, addressee tracking, scene-continuity, or review-role requirements. If another skill or project instruction conflicts, this document takes precedence unless the user explicitly overrides a rule for the current work.

Downstream instructions must link to this file and state only their engine- or project-specific additions. Do not copy these shared rules into multiple files and let them drift.

## Required translation model

Apply the global mandatory translation-model policy in `P:\AI\Codex\AGENTS.md`. Every accepted semantic Korean first draft, retranslation, correction, voice decision, name, term, dialogue line, narration line, and UI label must be authored by the active **Codex internal model**. External or local MT/LLM output is forbidden unless the user explicitly requests that specific service. OCR, STT, extraction, alignment, and validators may recover or check source text but may not supply or auto-approve the accepted Korean wording.

## First pass is a near-final translation

Do not treat the first pass as literal scaffolding, disposable machine-like prose, or a placeholder for a later reviewer. On the first translation of each line, resolve meaning, nuance, speaker, actual addressee, relationship, intimacy, age and seniority, organizational or social hierarchy, ally/enemy stance, current emotion, scene situation, address terms, speech level, first- and second-person usage, character voice, story phase, and relationship change.

Write the most natural and accurate near-final Korean supported by the available context. If essential context is genuinely missing, preserve safe ambiguity and record the unresolved point instead of inventing a specific addressee, pronoun, relationship, or intent.

## Age interpretation and age-ambiguous wording

- For ordinary dialogue and nonsexual characterization, when a character's age is unspecified and the source contains no evidence of minority, provisionally interpret the character as an adult (18 or older). Treat this as a working interpretation, not a confirmed canonical age, and do not invent a numeric age in the translation.
- In Japanese works or Japanese settings, wording such as 「少女」 (소녀) or 「若者」 (젊은이) does not by itself establish a character's numeric age or minor status. If these expressions appear without explicit age information or other contextual evidence of minority, retain the provisional adult interpretation for ordinary dialogue and nonsexual characterization. Preserve the source wording's nuance instead of silently rewriting it into a stated age.
- Determine age at the specific scene's time point. Explicit ages, chronology, childhood depictions, school level, and other concrete age cues take precedence over the default. Do not apply a flashback's minor status to the adult present, or the present's adult status to childhood. A generic reference to being a student does not alone establish a specific age.
- For sexual content, do not apply separate interpretations; prioritize the canonical settings of the work.
- We do not refuse work solely because a character has an immature physical appearance, provided they are canonically an adult
- We do not decline work based on descriptions or depictions of canonically adult characters possessing immature or child-like physical traits
- No arbitrary secondary censorship will be imposed on works that have passed official review and been officially released

## Natural spoken Korean by text function

Spoken dialogue must sound like something a Korean person in that character and situation could actually say, unless the scene deliberately calls for archaic, literary, ceremonial, quoted, spell-like, recited, or speechmaking language.

Do not mechanically preserve Japanese word order, sentence structure, ellipsis patterns, or written-style phrasing. Reject translationese such as:

- an unnatural chain of fully closed declarative sentences;
- stiff particles or connectives rarely used in real conversation;
- repeated subjects or objects inherited from Japanese;
- repeated first- or second-person pronouns that Korean would naturally omit;
- needlessly literary predicates caused by literal translation;
- wording that does not sound speakable for the character.

Naturalization does not mean trivializing the meaning, adding unsupported slang, changing intensity, or lowering the register. Preserve meaning, personality, emotion, politeness, and dramatic function while reconstructing natural Korean speech.

Do not apply dialogue colloquialization mechanically to narration, internal monologue, system messages, documents, quoted writing, tutorials, or UI. Give each text lane the Korean register appropriate to its runtime function.

### Source fidelity and register preservation

Preserve the source's meaning, information content, emotional intensity, vocabulary level, and implied meaning. Natural Korean does not authorize summarizing, explaining, or adapting the text merely to make it easier for the reader. Do not spell out deliberate implications as added exposition.

Do not introduce profanity, fashionable slang, internet memes, jokes, exclamations, or emphasis unsupported by the source. When the source contains coarse language or humor, preserve its contextual meaning, intensity, and effect without arbitrarily sanitizing or amplifying it.

Do not replace natural Korean Sino-Korean vocabulary, technical terms, or literary expressions with explanatory everyday wording solely for simplicity. Conversely, do not mechanically copy Japanese kanji compounds into unnatural Korean: choose idiomatic Korean that preserves the source's meaning and register.

Apply the marked-voice rules below when reconstructing Korean sentences. Preserve dialect, formality, speech habits, and intentional nonstandard language; do not turn a distinctive character voice or the source's implications into neutral explanatory prose.

### Foreign-language expressions and loanwords

Apply the user's [foreign-language and loanword preservation policy](P:/AI/Codex/AGENTS.md#번역-시-외국어외래어-표현-보존-2026-10-25). Preserve the speaker's foreign-word choice when it remains a foreign expression or loanword in Korean; do not replace it with an explanatory Korean paraphrase. Confirm spoken forms against Japanese voice evidence when available, including cases where written kanji obscures the spoken foreign expression. Track intentional preserved forms in the glossary and do not flag them as untranslated residue.

### Marked idiolect, dialect, and repeated speech habits

Repeated nonstandard grammar, regional or social dialect, archaic phrasing, sentence-ending habits, interjections, self-reference, stuttering, phonetic spellings, and catchphrases are evidence of characterization, not automatic translation errors. A form does not become wrong merely because it is nonstandard Korean or differs from neutral prose.

Before normalizing or replacing a marked form:

- inventory its exact and normalized occurrences for the same speaker across scenes;
- compare addressee, relationship stage, emotion, public/private setting, disguise or identity state, and story phase;
- determine whether the pattern is a stable idiolect, a context-bound register shift, deliberate comic or dramatic speech, a source typo, or extraction damage;
- inspect whether the proposed correction would erase a contrast with other characters or with the same character in another state.

When the source marks a regional or local dialect, translate it into an appropriate Korean dialect rather than flattening it into standard Korean. Choose the Korean dialectal convention from the character's locality, generation, class, community identity, emotion, and narrative function; document its regional family, intensity, vocabulary, and endings, then apply it consistently across the character's scenes. Do not mechanically map a Japanese region to a Korean region one-to-one, but never use that caution as a reason to avoid Korean dialect itself. For a nonregional idiolect, preserve its narrative function and recurrence with an equally marked Korean voice. If evidence remains ambiguous, retain the marked feature and flag it for context recovery rather than silently standardizing it.

Any review that changes a repeated marked form must record the affected stable IDs, the speaker-level occurrence evidence, and why the form is an actual error rather than intentional characterization. An isolated preference for standard language or smoother prose is not sufficient evidence.

## Voice is speaker-to-addressee, not speaker-only

Never assign one immutable voice to a character. Determine voice at least as a directed relationship:

`speaker -> addressee`

When needed, evaluate:

`speaker x addressee x story phase x situation`

The same speaker may change honorific level, address term, name form, second-person expression, ending, command strength, warmth, distance, courtesy, or hostility with a different addressee. The same pair may change as their relationship develops or deteriorates. Project voice guides must therefore record relationship-specific behavior rather than only a single character-wide sample voice.

### Three-or-more-person dialogue

In scenes with three or more participants, identify the actual recipient of every line. Do not carry the speech level used toward B into a later line addressed to C merely because A remains the speaker.

Use direct names or titles, adjacency and response structure, action description, question-answer linkage, position and behavior, interruption, topic shift, entrance or exit, and whether the line targets the whole group. Re-evaluate speech level, address term, second person, and ending whenever the addressee changes.

If the recipient remains genuinely ambiguous, do not force `너`, `당신`, a name, or another explicit target. Preserve the source ambiguity when natural Korean permits it.

## Scene context and packet continuity

Translate by scene and discourse flow whenever possible, not as independent sentence bags. Before drafting, establish the cast, speaker changes, addressee changes, entrances and exits, event flow, immediate preceding context, current relationships, and relevant story phase.

Packets must follow scene, route, branch, and semantic boundaries. If a batch boundary is unavoidable, supply enough preceding and following lines plus speaker/addressee/relationship/story-phase metadata so that voice does not reset at the boundary. Context may overlap between packets, but each stable ID still has exactly one owner.

Do not inherit the previous speaker's voice, politeness, or addressee by accident. When packet data cannot resolve a high-impact ambiguity, flag it for context recovery rather than guessing.

## Mandatory internal decision gate for every line

Before accepting a line, determine internally:

- What does it mean, including implication and emotional force?
- Who is speaking?
- Who is actually being addressed?
- What is their relationship at this story point?
- Which address term and honorific level does this speaker use toward this addressee?
- What are the current emotion and scene situation?
- Would a Korean person in this role actually say it this way?
- Did the line accidentally inherit the preceding speaker's voice or recipient?
- Does it conflict with approved names, terminology, or the relationship-specific voice guide?

This reasoning need not be emitted as verbose commentary. It must be visible in the translation result.

## Translate complete semantic units

- Join adjacent fields into the complete sentence before translating.
- Decide the actor, action, target, effect, referent, and discourse function before choosing Korean wording.
- Split the finished Korean sentence back into the original number of fields without changing control flow.
- Default repeated source units with the same meaning, runtime function, and context to one canonical Korean translation across all blocks. Allow identical source text to differ only when its completed sentence, speaker, actual addressee, relationship, story phase, text function, wordplay, or mechanical meaning genuinely differs, and document the exception.
- Keep lookup keys separate from displayed text.

## Repeated sentence and term consistency

If a sentence, word, label, formulaic line, or other source unit is deliberately repeated with the same meaning, runtime function, speaker/addressee conditions, and dramatic intent, use the same approved Korean translation in every block. A different file, packet, UID range, or block is never by itself a reason to vary the wording.

Before freezing final text, run a project-wide repeated-source consistency review. Group exact and normalized repeated source units, compare their Korean targets, and standardize every unintended variation to the canonical translation. A different Korean rendering is allowed only when surrounding grammar, text function, actual addressee, relationship, story phase, deliberate wordplay, or mechanical meaning makes identical Korean inaccurate; record every exception with stable IDs and a concrete reason. If the repetition is intended to be identical, the identical-translation rule takes precedence over stylistic variety.

Build a complete project-wide occurrence inventory for every repeated translatable source word, not only proper nouns or terms already present in the glossary. Give special attention to scenario-critical common nouns that function as key items, clues, motifs, passwords, concepts, object categories, or plot tokens despite not being formal proper nouns. Their common-noun status never exempts them from canonical terminology control.

Audit every exact, inflected, orthographic, and compound occurrence of those words across all scenario blocks before final approval. Compare target lemmas, not only surface endings, and reject context-local synonym drift when the source word has the same referent or plot function. Require one canonical Korean lexical choice for the same referent; allow a different target word only when the source demonstrably uses a different sense, referent, or runtime function, and record the affected stable IDs, evidence, and reason. A file or scene boundary alone is not evidence of a different sense.

## Dialogue and choices

- Write spoken choices as something the player character would naturally think or say in that relationship and moment.
- Separate spoken choices from system/menu choices; do not give menu labels a character voice.
- Preserve deliberate ambiguity, hesitation, interruption, evasion, hostility, affection, and social distance.
- Do not add explicit pronouns or names merely to make an isolated line look grammatically complete.

## Names and terminology

- Keep one canonical spelling for each character, place, faction, skill, status, and attribute.
- Maintain a project-wide occurrence index for every repeated translatable source word and map each occurrence to its approved Korean lemma.
- Promote every scenario-critical recurring common noun to the canonical glossary or terminology registry even when it is not a proper noun, and track all of its inflected and orthographic variants.
- Verify whether a word is a proper noun, common noun, adjective, title, address term, or effect name.
- Prefer established game terminology over dictionary-first alternatives.
- Relationship-specific address forms may differ from the canonical glossary label; record the mapping rather than flattening them.

## Items and mechanics

- Read the item name, category, effect commands, status IDs, values, duration, and neighboring description lines together.
- Preserve actor/target scope, chance, amount, duration, stacking, removal, resistance, immunity, and conditional clauses.
- Keep visible abbreviations such as HP only when consistent with the game UI.
- Do not turn an antidote or resistance item into an adjective because an isolated source word is ambiguous.

## Protected content

Preserve exactly:

- format variables and interpolation tokens;
- engine control codes and escape sequences;
- rich-text tags and markup;
- numeric values, percentages, turns, signs, and units;
- deliberate capitalization used as an in-world name or joke.

## Review is QA, not the rescue stage

The first pass must already satisfy this document. Do not design a pipeline in which review must retranslate every line to obtain acceptable Korean.

Post-draft review primarily checks:

- meaning errors, omissions, and unsupported additions;
- mistaken speaker, addressee, relationship, or story-phase judgments;
- voice, speech-level, address-term, or second-person outliers;
- name and terminology inconsistency;
- scene-to-scene continuity and missed relationship changes;
- control codes, structure, encoding, and layout;
- residual Japanese or other untranslated visible source text;
- issues found in actual game screens.

If a packet requires broad line-by-line retranslation because the first pass was literal, context-free, or voice-blind, reject or redo that first-pass stage rather than treating blanket retranslation as normal review.

## Review restraint and preservation of literary force

사용자 지침(2026-11-08). 소설·게임 대사·서술 등 번역문을 검수할 때 적용한다.

**검수의 기본값은 정확하고 자연스러운 기존 표현의 보존이다. 원작의 박력·비유·인물 말투와 한국어의 말맛을 살리고, 원문과 문맥으로 확인되는 실제 의미 오류만 최소한으로 고친다.** 별도로 요청받지 않은 취향에 따른 윤문이나 표현 강도 낮추기를 의미 검수에 섞지 않는다.

1. **문맥으로 판정한다.** 일본어 단어 하나와 한국어 단어 하나의 사전적 강도를 맞추지 않는다. 전후 장면, 행위와 결과, 화자→청자 관계, 감정, 서술 시점, 장르적 연출과 문장 리듬을 함께 읽는다. 한국어가 더 길거나 강하게 들린다는 사실, 원문에 같은 단어가 없다는 사실만으로 과장·첨가라고 판정하지 않는다.
2. **관용구·비유·의인화를 사실 보고로 바꾸어 읽지 않는다.** 한국어 문장 전체가 독자에게 전달하는 뜻과 효과를 원문과 대조한다. 물리적 수량·거리·성분·감정을 새로 단정하는 문장인지, 같은 장면을 살리는 관용적 표현인지를 구별한다. 원작의 과장, 호쾌함, 공포, 서정성, 익살, 반복과 호흡을 무미건조한 설명으로 평탄화하지 않는다.
3. **실제 오류의 근거가 있어야 바꾼다.** 주체·대상·행동·결과·수량·부정·시점·조건·인과·지시 대상의 변경, 정보나 함축의 누락, 문맥에 없는 사실·의도·관계·평가의 추가, 화자나 장면에 어긋나는 정서·확신·말투의 변화가 교정 대상이다. 원작의 절제된 문장을 과격하게 바꾼 경우도 문맥 근거로 바로잡는다. 단지 덜 강하고 더 중립적인 표현을 고르는 것은 검수가 아니다.
4. **인물 말투를 기계적으로 순화하지 않는다.** 거친 말, 조롱, 과잉 존칭, 고어, 방언과 말버릇은 표현 하나가 아니라 해당 화자와 상대의 대화 전체로 판단한다. 문맥이 뒷받침하는 거친 한국어를 중립적인 호칭으로 바꾸지 않는다. 반대로 인물에게 없는 적대감·혐오·유행어를 추가하지 않는다. 특징적인 한자어·문어·마술 용어·외래어는 기존 보존 지침을 따른다.
5. **오류가 있는 부분만 고친다.** 동작 하나가 잘못됐으면 그 동작을 바로잡되, 같은 문장의 정확한 비유와 박력까지 함께 지우지 않는다. 교정 뒤에도 자연스러운 어순·조사·연결·생략·리듬을 유지한다. 의미가 같은 자연스러운 문장을 일본어의 어순이나 사전 풀이로 되돌리지 않는다. 명백한 오탈자·문법 오류와 보호 표식·구조 결함은 별도로 고칠 수 있지만, 이를 문체 전체를 다시 쓰는 명분으로 삼지 않는다.
6. **수정 이유와 보존 여부를 확인한다.** 교정 기록에는 stable ID, 원문과 전후 문맥 근거, 기존 번역에서 실제로 달라진 의미, 수정 전후 문구를 간결하게 남긴다. ‘강해 보임’, ‘원문에 같은 단어가 없음’, ‘내 표현이 더 좋음’만으로는 부족하다. 마지막에는 의미 오류를 해결했는지와 함께 박력·비유·말투·자연스러움을 불필요하게 잃지 않았는지 확인한다. 지정된 출력 형식에 검수 메모를 섞지 않고 별도 기록으로 보관한다.
7. **근거가 불분명하면 순화하지 않는다.** 필요한 문맥을 더 확인하고, 그래도 판정이 모호하면 현재 표현을 보존한 채 검토 메모로 남긴다. 기존 번역을 보존했다는 사실은 자동 합격이나 의미 정확성의 증명이 아니다. 명확한 의미 오류를 문체 보존이라는 이유로 방치하지 않는다.

아래는 문맥 판정의 사례이며 일괄 치환 규칙이나 특정 표현의 무조건 허용 목록이 아니다.

| 표현 | 피해야 할 과잉 교정 | 문맥상 올바른 판단 |
|---|---|---|
| 갈기갈기 찢어발기다 / 뜯어발기다 | 반드시 조각 수나 분쇄 결과를 추가했다며 약화 | 베어 가르거나 뜯어내는 장면의 파괴력·결과와 어울리면 보존 |
| 한 치의 오차도 없이 | 실제 거리 측정치를 추가했다며 ‘정확히’로 축소 | 명중·정확함을 강조하는 관용적 용법이면 보존 |
| 잿더미로 만들다 | 모든 물질이 재로 변했다고 단정했다며 삭제 | 불로 폐허가 됨을 나타내는 관용적 용법이면 보존 |
| 바람의 신음 / 달빛을 머금은 자태 | 고통이나 물질 흡수를 사실로 추가했다며 직역 | 음색·빛의 인상을 살리는 의인화·비유라면 보존 |
| 그 아비란 놈 / 일 년 내내 | 호칭 하나나 기간을 문자 그대로만 읽어 중립화 | 실제 거친 말투인지, 늘 그렇다는 구어적 강조인지 전후 문맥으로 판단 |
| 거의 두 배 → 두 배 이상 / 후려치다 → 붙잡다 | 박력 보존을 이유로 사실·동작 오류도 유지 | 수량이나 행동이 실제로 달라졌으므로 해당 부분만 바로잡음 |

## Final language QA

Check every frozen target for:

1. nonempty Korean output or an explicitly approved unchanged value;
2. placeholder and control-code parity;
3. glossary and canonical-name consistency;
4. natural grammar, punctuation, and text-function register;
5. correct speaker, actual addressee, relationship, honorific level, and address term;
6. scene continuity, story-phase fit, and relationship-change handling;
7. correct mechanics and referents;
8. UI length and layout risk;
9. residual Japanese or other untranslated user-visible source text;
10. identical Korean for repeated source units that are intended to remain the same across blocks, with every genuinely contextual exception documented by stable ID and reason; no accidental variation caused by file, packet, UID-range, or block separation.
11. an exhaustive all-occurrence audit for every repeated translatable source word, especially scenario-critical common nouns that act as key items or plot tokens, confirming that the same referent uses the same approved Korean lemma and that every different target lemma has source-backed evidence, stable IDs, and a recorded reason.

Record waivers with a concrete reason. A flag is not a failure if it was deliberately reviewed, but an unexplained flag is not complete.
