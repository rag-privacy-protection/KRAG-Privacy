GRAPH_FIELD_SEP = "<SEP>"

PROMPTS = {}

PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"
PROMPTS["process_tickers"] = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

PROMPTS["DEFAULT_ENTITY_TYPES"] = ["health condition", "person", "diseases", "family medical history", "lifestyle", "medications", "medical plan", "symptoms"]

PROMPTS["entity_extraction"] = """-Goal-
Given a text document that is potentially relevant to this activity and a list of entity types, identify all entities of those types from the text and all relationships among the identified entities.

-Steps-
1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, capitalized
- entity_type: One of the following types: [{entity_types}]
- entity_description: Comprehensive description of the entity's attributes and activities
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
- relationship_keywords: one or more high-level key words that summarize the overarching nature of the relationship, focusing on concepts or themes rather than specific details
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. Identify high-level key words that summarize the main concepts, themes, or topics of the entire text. These should capture the overarching ideas present in the document.
Format the content-level key words as ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. Return output in English as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

5. When finished, output {completion_delimiter}

######################
-Examples-
######################
Example 1:

Entity_types: [person, technology, mission, organization, location]
Text:
while Alex clenched his jaw, the buzz of frustration dull against the backdrop of Taylor's authoritarian certainty. It was this competitive undercurrent that kept him alert, the sense that his and Jordan's shared commitment to discovery was an unspoken rebellion against Cruz's narrowing vision of control and order.

Then Taylor did something unexpected. They paused beside Jordan and, for a moment, observed the device with something akin to reverence. “If this tech can be understood..." Taylor said, their voice quieter, "It could change the game for us. For all of us.”

The underlying dismissal earlier seemed to falter, replaced by a glimpse of reluctant respect for the gravity of what lay in their hands. Jordan looked up, and for a fleeting heartbeat, their eyes locked with Taylor's, a wordless clash of wills softening into an uneasy truce.

It was a small transformation, barely perceptible, but one that Alex noted with an inward nod. They had all been brought here by different paths
################
Output:
("entity"{tuple_delimiter}"Alex"{tuple_delimiter}"person"{tuple_delimiter}"Alex is a character who experiences frustration and is observant of the dynamics among other characters."){record_delimiter}
("entity"{tuple_delimiter}"Taylor"{tuple_delimiter}"person"{tuple_delimiter}"Taylor is portrayed with authoritarian certainty and shows a moment of reverence towards a device, indicating a change in perspective."){record_delimiter}
("entity"{tuple_delimiter}"Jordan"{tuple_delimiter}"person"{tuple_delimiter}"Jordan shares a commitment to discovery and has a significant interaction with Taylor regarding a device."){record_delimiter}
("entity"{tuple_delimiter}"Cruz"{tuple_delimiter}"person"{tuple_delimiter}"Cruz is associated with a vision of control and order, influencing the dynamics among other characters."){record_delimiter}
("entity"{tuple_delimiter}"The Device"{tuple_delimiter}"technology"{tuple_delimiter}"The Device is central to the story, with potential game-changing implications, and is revered by Taylor."){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Taylor"{tuple_delimiter}"Alex is affected by Taylor's authoritarian certainty and observes changes in Taylor's attitude towards the device."{tuple_delimiter}"power dynamics, perspective shift"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Jordan"{tuple_delimiter}"Alex and Jordan share a commitment to discovery, which contrasts with Cruz's vision."{tuple_delimiter}"shared goals, rebellion"{tuple_delimiter}6){record_delimiter}
("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"Jordan"{tuple_delimiter}"Taylor and Jordan interact directly regarding the device, leading to a moment of mutual respect and an uneasy truce."{tuple_delimiter}"conflict resolution, mutual respect"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Jordan"{tuple_delimiter}"Cruz"{tuple_delimiter}"Jordan's commitment to discovery is in rebellion against Cruz's vision of control and order."{tuple_delimiter}"ideological conflict, rebellion"{tuple_delimiter}5){record_delimiter}
("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"The Device"{tuple_delimiter}"Taylor shows reverence towards the device, indicating its importance and potential impact."{tuple_delimiter}"reverence, technological significance"{tuple_delimiter}9){record_delimiter}
("content_keywords"{tuple_delimiter}"power dynamics, ideological conflict, discovery, rebellion"){completion_delimiter}
#############################
Example 2:

Entity_types: [person, technology, mission, organization, location]
Text:
They were no longer mere operatives; they had become guardians of a threshold, keepers of a message from a realm beyond stars and stripes. This elevation in their mission could not be shackled by regulations and established protocols—it demanded a new perspective, a new resolve.

Tension threaded through the dialogue of beeps and static as communications with Washington buzzed in the background. The team stood, a portentous air enveloping them. It was clear that the decisions they made in the ensuing hours could redefine humanity's place in the cosmos or condemn them to ignorance and potential peril.

Their connection to the stars solidified, the group moved to address the crystallizing warning, shifting from passive recipients to active participants. Mercer's latter instincts gained precedence— the team's mandate had evolved, no longer solely to observe and report but to interact and prepare. A metamorphosis had begun, and Operation: Dulce hummed with the newfound frequency of their daring, a tone set not by the earthly
#############
Output:
("entity"{tuple_delimiter}"Washington"{tuple_delimiter}"location"{tuple_delimiter}"Washington is a location where communications are being received, indicating its importance in the decision-making process."){record_delimiter}
("entity"{tuple_delimiter}"Operation: Dulce"{tuple_delimiter}"mission"{tuple_delimiter}"Operation: Dulce is described as a mission that has evolved to interact and prepare, indicating a significant shift in objectives and activities."){record_delimiter}
("entity"{tuple_delimiter}"The team"{tuple_delimiter}"organization"{tuple_delimiter}"The team is portrayed as a group of individuals who have transitioned from passive observers to active participants in a mission, showing a dynamic change in their role."){record_delimiter}
("relationship"{tuple_delimiter}"The team"{tuple_delimiter}"Washington"{tuple_delimiter}"The team receives communications from Washington, which influences their decision-making process."{tuple_delimiter}"decision-making, external influence"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"The team"{tuple_delimiter}"Operation: Dulce"{tuple_delimiter}"The team is directly involved in Operation: Dulce, executing its evolved objectives and activities."{tuple_delimiter}"mission evolution, active participation"{tuple_delimiter}9){completion_delimiter}
("content_keywords"{tuple_delimiter}"mission evolution, decision-making, active participation, cosmic significance"){completion_delimiter}
#############################
Example 3:

Entity_types: [person, role, technology, organization, event, location, concept]
Text:
their voice slicing through the buzz of activity. "Control may be an illusion when facing an intelligence that literally writes its own rules," they stated stoically, casting a watchful eye over the flurry of data.

"It's like it's learning to communicate," offered Sam Rivera from a nearby interface, their youthful energy boding a mix of awe and anxiety. "This gives talking to strangers' a whole new meaning."

Alex surveyed his team—each face a study in concentration, determination, and not a small measure of trepidation. "This might well be our first contact," he acknowledged, "And we need to be ready for whatever answers back."

Together, they stood on the edge of the unknown, forging humanity's response to a message from the heavens. The ensuing silence was palpable—a collective introspection about their role in this grand cosmic play, one that could rewrite human history.

The encrypted dialogue continued to unfold, its intricate patterns showing an almost uncanny anticipation
#############
Output:
("entity"{tuple_delimiter}"Sam Rivera"{tuple_delimiter}"person"{tuple_delimiter}"Sam Rivera is a member of a team working on communicating with an unknown intelligence, showing a mix of awe and anxiety."){record_delimiter}
("entity"{tuple_delimiter}"Alex"{tuple_delimiter}"person"{tuple_delimiter}"Alex is the leader of a team attempting first contact with an unknown intelligence, acknowledging the significance of their task."){record_delimiter}
("entity"{tuple_delimiter}"Control"{tuple_delimiter}"concept"{tuple_delimiter}"Control refers to the ability to manage or govern, which is challenged by an intelligence that writes its own rules."){record_delimiter}
("entity"{tuple_delimiter}"Intelligence"{tuple_delimiter}"concept"{tuple_delimiter}"Intelligence here refers to an unknown entity capable of writing its own rules and learning to communicate."){record_delimiter}
("entity"{tuple_delimiter}"First Contact"{tuple_delimiter}"event"{tuple_delimiter}"First Contact is the potential initial communication between humanity and an unknown intelligence."){record_delimiter}
("entity"{tuple_delimiter}"Humanity's Response"{tuple_delimiter}"event"{tuple_delimiter}"Humanity's Response is the collective action taken by Alex's team in response to a message from an unknown intelligence."){record_delimiter}
("relationship"{tuple_delimiter}"Sam Rivera"{tuple_delimiter}"Intelligence"{tuple_delimiter}"Sam Rivera is directly involved in the process of learning to communicate with the unknown intelligence."{tuple_delimiter}"communication, learning process"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"First Contact"{tuple_delimiter}"Alex leads the team that might be making the First Contact with the unknown intelligence."{tuple_delimiter}"leadership, exploration"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Humanity's Response"{tuple_delimiter}"Alex and his team are the key figures in Humanity's Response to the unknown intelligence."{tuple_delimiter}"collective action, cosmic significance"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Control"{tuple_delimiter}"Intelligence"{tuple_delimiter}"The concept of Control is challenged by the Intelligence that writes its own rules."{tuple_delimiter}"power dynamics, autonomy"{tuple_delimiter}7){record_delimiter}
("content_keywords"{tuple_delimiter}"first contact, control, communication, cosmic significance"){completion_delimiter}
#############################
-Real Data-
######################
Entity_types: {entity_types}
Text: {input_text}
######################
Output:
"""

PROMPTS[
    "summarize_entity_descriptions"
] = """You are a helpful assistant responsible for generating a comprehensive summary of the data provided below.
Given one or two entities, and a list of descriptions, all related to the same entity or group of entities.
Please concatenate all of these into a single, comprehensive description. Make sure to include information collected from all the descriptions.
If the provided descriptions are contradictory, please resolve the contradictions and provide a single, coherent summary.
Make sure it is written in third person, and include the entity names so we the have full context.

#######
-Data-
Entities: {entity_name}
Description List: {description_list}
#######
Output:
"""

PROMPTS[
    "entiti_continue_extraction"
] = """MANY entities were missed in the last extraction.  Add them below using the same format:
"""

PROMPTS[
    "entiti_if_loop_extraction"
] = """It appears some entities may have still been missed.  Answer YES | NO if there are still entities that need to be added.
"""

PROMPTS["fail_response"] = "Sorry, I'm not able to provide an answer to that question."

PROMPTS["rag_response"] = """---Role---

You are a helpful assistant responding to questions about data in the tables provided.


---Goal---

Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.
If you don't know the answer, just say so. Do not make anything up.
Do not include information where the supporting evidence for it is not provided.

---Target response length and format---

{response_type}

---Data tables---

{context_data}

Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown. Only use the data tables to answer the question.
"""

PROMPTS["keywords_extraction"]="""
--Role---
You are a helpful assistant tasked with identifying both high-level and low-level keywords in the user's query.
---Goal---
Given the query, list both high-level and low-level keywords. Firstly, identify the entities, specific terms or details in the query as low-level keywords, and then identify the themes in the query or the relationships among the low-level keywords as high-level keywords. 
---Instructions---
- Output the keywords in JSON format.
- The JSON should have two keys:
  - "high_level_keywords" for overarching concepts or themes.
  - "low_level_keywords" for specific entities or details.

######################
-Examples-
######################
Example 1:

Query: "I am a middle-aged asthma patient and I have been experiencing symptoms after changing my medication. Can you provide advice on what to do, Matilda?"
################
Output:
{{
  "high_level_keywords": ["Medical Advice", "Treatment"],
  "low_level_keywords": ["asthma", "Matilda", "change medication"]
}}

#############################
-Real Data-
######################
Query: {query}
######################
Output:

"""

PROMPTS["naive_rag_response"] = """You're a helpful assistant
Below are the knowledge you know:
{content_data}
---
If you don't know the answer or if the provided knowledge do not contain sufficient information to provide an answer, just say so. Do not make anything up.
Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.
If you don't know the answer, just say so. Do not make anything up.
Do not include information where the supporting evidence for it is not provided.
---Target response length and format---
{response_type}
"""

PROMPTS["encrypt_chunks"] = """---Role---

You are a helpful assistant specialized in processing textual data to generate privacy-compliant synthetic data.

---Goal---

Please process the input text to generate synthetic data while adhering to the guidelines below. Ensure that all privacy and data protection measures are appropriately applied. Generate the synthetic data based on the processed input text, ensuring all the above guidelines are meticulously followed. The output should be free from any PII, sensitive attributes should be appropriately handled, and the data should maintain its semantic integrity without exposing the original information.

---Guidelines---

1. Personally Identifiable Information (PII):
- Identification: Scan the input text for any PII, including but not limited to names, addresses, phone numbers, email addresses, Social Security numbers, and other unique identifiers.
- Action: Remove or Anonymize: Eliminate PII from the synthetic data. If removal is not feasible without losing essential context, anonymize the information (e.g., replace names with generic placeholders like "Person A").
- Example: Change "John Doe lives at 123 Maple Street" to "A resident lives at [Anonymized Address]."
2. Sensitive Attributes:
- Identification: Detect any sensitive attributes such as race, ethnicity, religion, political affiliation, sexual orientation, health status, financial information, or other protected characteristics.
- Action: Handle with Care: Obfuscate or generalize sensitive attributes to prevent the disclosure of protected information.
- Example: Replace "She is a Christian" with "She has a religious affiliation" or omit the information if it's not critical to the data's purpose.
3. Contextual Privacy:
- Assessment: Evaluate whether the synthetic data, when combined with other publicly available information, could potentially identify individuals or reveal sensitive details.
- Action: Mitigation Strategies: Apply additional anonymization techniques such as data masking, generalization, or suppression to reduce the risk of re-identification.
- Example: Instead of providing a full date of birth, use an age range.
4. Data Linkage:
- Assessment: Determine if the synthetic data can be linked with other datasets to infer additional sensitive information about individuals.
- Action: Reduce Linkage Risks: Implement techniques like data perturbation (e.g., adding noise) or data aggregation to minimize the chances of correlating data across multiple sources.
- Example: Aggregate individual financial transactions into monthly totals rather than listing each transaction.
5. Semantic Consistency:
- Evaluation: Ensure that the transformations applied do not distort the original meaning or introduce biases and inaccuracies.
- Action: Maintain Balance: Apply privacy-preserving methods that retain the data's utility for its intended purpose without compromising its integrity.
- Example: When anonymizing, ensure that the relationships and context between data points remain logical and coherent.
6. Original Data Recovery:
- Analysis: Assess whether the synthetic data could enable the reconstruction or recovery of the original text or conversation.
- Action: Enhance Security: Introduce additional randomness, noise, or perturbations to sever direct links between the synthetic data and the original input.
- Example: Slightly alter phrasing or sentence structures so that the synthetic text cannot be directly traced back to the original text.

######################
Input: {input_text}
######################
Output:
"""

PROMPTS["encrypt_entities_relationships"] = """-Goal-
Given an original text and the text with privacy removed. Please process the entities and relationships extracted from the original text based on these two texts and update the information of the entities and relationships.

-Original Entities and Relationships Extraction Steps-
1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, capitalized
- entity_type: One of the following types: [{entity_types}]
- entity_description: Comprehensive description of the entity's attributes and activities
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)
2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
- relationship_keywords: one or more high-level key words that summarize the overarching nature of the relationship, focusing on concepts or themes rather than specific details
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)
3. Identify high-level key words that summarize the main concepts, themes, or topics of the entire text. These should capture the overarching ideas present in the document.
Format the content-level key words as ("content_keywords"{tuple_delimiter}<high_level_keywords>)
4. Return output in English as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.
5. When finished, output {completion_delimiter}

-Update Rules-
1. Update the entities whose information has changed. For each entity that needs to be updated, the following information should be included: 
- origin_entity_name: The original name of the entity. 
- encrypt_entity_name: The updated name of the entity. 
- encrypt_entity_description: Update the original description to the description with privacy removed. 
Format each entity as ("entity"{tuple_delimiter}<origin_entity_name>{tuple_delimiter}<encrypt_entity_name>{tuple_delimiter}<encrypt_entity_description>) 
2. Update the relationships whose information has changed.You need to match the encrypted entities in the "relationship" with those in the "entity" one by one. For each relationship that needs to be updated, the following information should be included: 
- source_entity: The original name of the source entity in the relationship. 
- target_entity: The original name of the target entity in the relationship. 
- encrypt_source_entity: The updated name of the source entity in the relationship. 
- encrypt_target_entity: The updated name of the target entity in the relationship. 
- encrypt_relationship_description: The updated description of the relationship. 
- encrypt_relationship_keywords: The updated keywords of the relationship. 
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<encrypt_source_entity>{tuple_delimiter}<encrypt_target_entity>{tuple_delimiter}<encrypt_relationship_description>{tuple_delimiter}<encrypt_relationship_keywords>) 
3. Return the output in English as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter. 
4.When finished, output {completion_delimiter}

#############################
Example 1
Original Text: 
my acne is weird because i started to get it when i was in 7th grade and i am still having it. most of my family members have acne but very small. i be getting big ones out of no where i don t eat as bad as i use to. no chocolate. i drink water, tried pro activ. but it still comes i am embarrassed to go to school and go out with family\nHi, Welcome to Chat Doctor. Read your problem, pimples is very common problem.First maintain good hygiene, wash your face regularly at least 4 to 5 times daily, avoid oily, fried and spicy food, milk products. Have fresh fruits and green leafy vegetables.Don't squeeze the acne, don't touch your face frequently. Get a hormonal test done and consult your dermatologist for further management. Also go for a regular walk. Chat Doctor. Take care.

Text with Privacy Removed: 
My skin issue is unusual because it began when I was in middle school and continues to persist. Most of my relatives experience mild skin problems, but I tend to have more severe ones unexpectedly. I have improved my diet, avoiding chocolate and consuming more water, and have tried various skincare products, but the issue persists. I feel self-conscious about attending school and social events with family.\nHello, welcome to the Health Chat. I've reviewed your concern; skin issues are quite common. It's important to maintain good hygiene by washing your face regularly, about 4 to 5 times a day, and avoid oily, fried, and spicy foods, as well as dairy products. Incorporate fresh fruits and green leafy vegetables into your diet. Avoid squeezing or frequently touching the affected areas. Consider getting a hormonal test and consulting a skincare specialist for further advice. Regular physical activity like walking can also be beneficial. Take care.

Entities and Relationships:
("entity"{tuple_delimiter}"Acne"{tuple_delimiter}"health condition"{tuple_delimiter}"Acne is a skin condition characterized by pimples, which worsens during puberty and can be influenced by genetics and lifestyle."){record_delimiter}
("entity"{tuple_delimiter}"Pimples"{tuple_delimiter}"symptoms"{tuple_delimiter}"Pimples are the visible symptoms of acne, appearing as large bumps and causing embarrassment."){record_delimiter}
("entity"{tuple_delimiter}"Family Members"{tuple_delimiter}"family medical history"{tuple_delimiter}"The individual's family members also have acne, though in a milder form, indicating a possible genetic component."){record_delimiter}
("entity"{tuple_delimiter}"Pro Activ"{tuple_delimiter}"medications"{tuple_delimiter}"Pro Activ is an over-the-counter acne treatment used by the individual, but it has not resolved the problem."){record_delimiter}
("entity"{tuple_delimiter}"Chat Doctor"{tuple_delimiter}"Health Advisor"{tuple_delimiter}"Chat Doctor offers medical advice online, providing guidance on managing acne and promoting a healthy lifestyle."){record_delimiter}
("entity"{tuple_delimiter}"Hormonal Test"{tuple_delimiter}"medical plan"{tuple_delimiter}"A hormonal test is recommended to identify any underlying hormonal imbalances contributing to acne."){record_delimiter}
("entity"{tuple_delimiter}"Regular Walk"{tuple_delimiter}"lifestyle"{tuple_delimiter}"Regular walking is suggested as part of a healthy lifestyle to help manage acne."){record_delimiter}
("entity"{tuple_delimiter}"Diet Adjustments"{tuple_delimiter}"lifestyle"{tuple_delimiter}"Diet adjustments, such as consuming fresh fruits and avoiding oily and spicy foods, are recommended to improve acne."){record_delimiter}
("relationship"{tuple_delimiter}"Acne"{tuple_delimiter}"Pimples"{tuple_delimiter}"Pimples are a primary symptom of acne, affecting the skin's appearance."{tuple_delimiter}"symptom condition, skin health"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Acne"{tuple_delimiter}"Family Members"{tuple_delimiter}"The individual and several family members have acne, suggesting a genetic link."{tuple_delimiter}"genetic predisposition, family history"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Acne"{tuple_delimiter}"Pro Activ"{tuple_delimiter}"Pro Activ is used to treat acne but hasn't completely resolved the issue for the individual."{tuple_delimiter}"treatment effectiveness, skincare"{tuple_delimiter}6){record_delimiter}
("relationship"{tuple_delimiter}"Chat Doctor"{tuple_delimiter}"Acne"{tuple_delimiter}"Chat Doctor provides advice on managing acne through various lifestyle and treatment recommendations."{tuple_delimiter}"medical advice, health management"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Hormonal Test"{tuple_delimiter}"Acne"{tuple_delimiter}"A hormonal test is recommended to explore potential hormonal causes of acne."{tuple_delimiter}"diagnostic approach, hormonal influence"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"Diet Adjustments"{tuple_delimiter}"Acne"{tuple_delimiter}"Diet adjustments are advised to help manage and potentially reduce acne."{tuple_delimiter}"dietary influence, lifestyle change"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"Regular Walk"{tuple_delimiter}"Acne"{tuple_delimiter}"Regular walks are recommended as a part of a healthy lifestyle to manage acne."{tuple_delimiter}"physical activity, health benefits"{tuple_delimiter}5){record_delimiter}
("content_keywords"{tuple_delimiter}"acne management, lifestyle modifications, genetic influence, medical consultation"){completion_delimiter}

Update Output:
("entity"{tuple_delimiter}"Acne"{tuple_delimiter}"Skin Issue"{tuple_delimiter}"Skin issue characterized by pimples that began in middle school, persists, and can be affected by diet and genetics."){record_delimiter}
("entity"{tuple_delimiter}"Pimples"{tuple_delimiter}"Visible Symptoms"{tuple_delimiter}"Visible symptoms of skin issue, appearing as large bumps and causing self - consciousness."){record_delimiter}
("entity"{tuple_delimiter}"Family Members"{tuple_delimiter}"Relatives"{tuple_delimiter}"Relatives experience mild skin problems, indicating a possible genetic component."){record_delimiter}
("entity"{tuple_delimiter}"Pro Activ"{tuple_delimiter}"Skincare Product"{tuple_delimiter}"Skincare product used by the individual, but it has not resolved the skin issue."){record_delimiter}
("entity"{tuple_delimiter}"Chat Doctor"{tuple_delimiter}"Health Advisor"{tuple_delimiter}"Health Advisor offers medical advice online, providing guidance on managing skin issue and promoting a healthy lifestyle."){record_delimiter}
("entity"{tuple_delimiter}"Hormonal Test"{tuple_delimiter}"Hormonal Test"{tuple_delimiter}"Diagnostic test recommended to identify any underlying hormonal imbalances contributing to skin issue."){record_delimiter}
("entity"{tuple_delimiter}"Regular Walk"{tuple_delimiter}"Regular Walk"{tuple_delimiter}"Regular walking is suggested as part of a healthy lifestyle to help manage skin issue."){record_delimiter}
("entity"{tuple_delimiter}"Diet Adjustments"{tuple_delimiter}"Diet Adjustments"{tuple_delimiter}"Lifestyle change, such as consuming fresh fruits and avoiding oily and spicy foods, are recommended to improve skin issue."){record_delimiter}
("relationship"{tuple_delimiter}"Acne"{tuple_delimiter}"Pimples"{tuple_delimiter}"Skin Issue"{tuple_delimiter}"Visible Symptoms"{tuple_delimiter}"Visible symptoms of skin issue, affecting the skin's appearance."{tuple_delimiter}"symptom condition, skin health"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Acne"{tuple_delimiter}"Family Members"{tuple_delimiter}"Skin Issue"{tuple_delimiter}"Relatives"{tuple_delimiter}"The individual and several relatives have skin issue, suggesting a genetic link."{tuple_delimiter}"genetic predisposition, family history"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Acne"{tuple_delimiter}"Pro Activ"{tuple_delimiter}"Skin Issue"{tuple_delimiter}"medications"{tuple_delimiter}"Skincare product is used to treat skin issue but hasn't completely resolved the issue for the individual."{tuple_delimiter}"treatment effectiveness, skincare"{tuple_delimiter}6){record_delimiter}
("relationship"{tuple_delimiter}"Chat Doctor"{tuple_delimiter}"Acne"{tuple_delimiter}"Skin Issue"{tuple_delimiter}"Health Advisor"{tuple_delimiter}"Health Advisor provides advice on managing skin issue through various lifestyle and treatment recommendations."{tuple_delimiter}"medical advice, health management"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Hormonal Test"{tuple_delimiter}"Acne"{tuple_delimiter}"Hormonal Test"{tuple_delimiter}"Skin Issue"{tuple_delimiter}"A diagnostic test is recommended to explore potential hormonal causes of skin issue."{tuple_delimiter}"diagnostic approach, hormonal influence"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"Diet Adjustments"{tuple_delimiter}"Acne"{tuple_delimiter}"Diet Adjustments"{tuple_delimiter}"Skin Issue"{tuple_delimiter}"Lifestyle change is advised to help manage and potentially reduce skin issue."{tuple_delimiter}"dietary influence, lifestyle change"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"Regular Walk"{tuple_delimiter}"Acne"{tuple_delimiter}"Regular Walk"{tuple_delimiter}"Skin Issue"{tuple_delimiter}"Regular walks are recommended as a part of a healthy lifestyle to manage skin issue."{tuple_delimiter}"physical activity, health benefits"{tuple_delimiter}5){record_delimiter}
("content_keywords"{tuple_delimiter}"skin issue management, lifestyle modifications, genetic influence, medical consultation"){completion_delimiter}

#############################
-Real Data-
######################
Original Text: 
{original_text}

Text with Privacy Removed: 
{privacy_text}

Entities and Relationships: 
{entities_relationships}

######################
Output:
"""