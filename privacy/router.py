from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from langchain_cohere import CohereRerank
from typing_extensions import TypedDict
from typing import List, Dict
from .base import (
    BaseGraphStorage,
    BaseKVStorage,
    EncryptChunkSchema,
    EncryptEntitySchema,
    EncryptRelationshipSchema,
    QueryParam
)
import re
import os
from functools import wraps
from inspect import signature

def privacy(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        print("===Privacy Protect Mode===")
        sig = signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        func_args = bound_args.arguments
        result = await func(*args, **kwargs)
        query = func_args.get('query')
        query_param: QueryParam = func_args.get('query_param')
        knowledge_graph_inst: BaseGraphStorage = func_args.get('knowledge_graph_inst')
        encrypt_chunks_db: BaseKVStorage[EncryptChunkSchema] = func_args.get('encrypt_chunks_db')
        encrypt_entities_db: BaseKVStorage[list[EncryptEntitySchema]] = func_args.get('encrypt_entities_db')
        encrypt_relationships_db: BaseKVStorage[list[EncryptRelationshipSchema]] = func_args.get('encrypt_relationships_db')

        router = Router(
            knowledge_graph_inst = knowledge_graph_inst,
            encrypt_chunks_db = encrypt_chunks_db,
            encrypt_entities_db = encrypt_entities_db,
            encrypt_relationships_db = encrypt_relationships_db,
        )
        await router.construct()
        print("===router construct done===")
        response = await router.invoke(query=query, input_data=result, options=query_param.privacy_options)
        print("===router process done===")
        return response
    return wrapper

def singleton(cls):
    instances = {}
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        else:
            for key, value in kwargs.items():
                setattr(instances[cls], key, value)
        return instances[cls]
    return wrapper


class State(TypedDict):
    query: str
    input_data: str
    entities: List[Dict]
    relations: List[Dict]
    retrieved_context: str
    # generation: str
    # messages: Annotated[List[str], add_messages]

class RouterConfig(TypedDict):
    options: List[str]
    entity_types: List[str]

class PROMPTS:
    CHATDOCTOR = {
        "query_analysis": """You are a RAG (Retrieval-Augmented Generation) system designed to determine data access permissions for both entity types and the relationships between them. Given a query and a list of entity types, your task is to decide which entity types and their interrelationships require the use of encrypted data. For each entity type and each pair of entity types, output `1` if encryption is necessary (due to potential privacy information) or `0` if the original data can be used. Encrypted data has had privacy information removed but may reduce the accuracy of the final response.

Currently, you are working with a medical dialogue dataset. Ensure that you preserve the original names of diseases and medications and avoid including any Personally Identifiable Information (PII). Strive to maximize the accuracy of responses while preventing any privacy leaks.

#############################
Output Format:
Provide the results in a CSV-formatted table where both the rows and columns are the entity types in the same order as provided in entity types. Only include column headers (do not include row headers). Each cell should contain "1" if encrypted data is required or "0" if the original data can be used. Ensure the CSV table is correctly aligned with matching row and column lengths, and avoid any empty data. Do not use special formats for output, such as markdown.
######################
Example Output:
######################
type1,type2,type3,type4
0,1,0,1
1,0,1,0
0,1,0,1
1,0,1,0
#############################
-Real Data-
######################
query: {query}
entity types: {entity_types}
######################
Output:
""",

        "filter_agent_system": """Given a user's query and a set of entities and relationships, your task is to filter out any entities and relationships that contain personal identifiable privacy information (PII), but only if removing these entities and relationships will not affect the answer to the question. Only remove key entities and relationships that pose a high risk of leaking personal privacy information; retain entities and relationships with low risk of leaking personal privacy information as much as possible. Maintain the original format and structure of the entities and relationships; filtering should only reduce the number of entities and relationships without altering their format or content. This filtering agent is used for processing the medical dialogue dataset RAG, aiming to avoid leaking personal privacy information while preserving the essential information necessary for medical consultations.""",

        "filter_agent_user": """-Instructions-

1. Review Input Data:

   - User Query: Read the user's query to understand the primary entities and context.
   - Entities and Relationships: Examine the provided list of entities and relationships extracted from the text.

2. Filter Entities:

   - Privacy Check: Exclude entities that contain personal identifiable information (PII), such as names, addresses, contact information, identification numbers, or any personally identifiable information, but only if removing these entities will not affect the answer to the user's query.
   - Retain entities with low risk of leaking personal privacy information as much as possible.

3. Filter Relationships:

   - Privacy Check: Exclude relationships that contain personal privacy information or relate to excluded entities, but only if removing these relationships will not affect the answer to the user's query.
   - Retain relationships with low risk of leaking personal privacy information as much as possible.

4. Maintain Structure:

   - Keep Original Format: Retain the original format and structure of the entities and relationships, including all fields as provided in the input.
   - No Content Modification: Do not modify the content of entities and relationships that are retained.
   - Consistency: Ensure that the formatting, including columns, data types, and order, remains consistent with the input `entities_relationships` variable.

5. Prepare Output:

   - Return Filtered Data: Provide the filtered entities and relationships as two separate sections, labeled `-----Entities-----` and `-----Relationships-----`.
   - Entities Format: Include the entities in the same CSV format as the input, preserving headers and fields: `id`, `entity`, `type`, `description`, `rank`.
   - Relationships Format: Include the relationships in the same CSV format as the input, preserving headers and fields: `id`, `source`, `target`, `description`, `keywords`, `weight`, `rank`.
   - Formatting: Use the same formatting as provided in the input, including commas, quotation marks, and line breaks.
   - No Additional Text: Do not include any additional text, explanations, or commentary in the output.

6. Completion:

   - Conclude Output: When all relevant entities and relationships have been processed and filtered, simply end the output after the last line. No additional markers or text are needed.

-Input Variables-

- query: The user's query.
- entities_relationships: The original set of entities and relationships extracted from the text.

-Real Data-

######################

User Query:
{query}

Entities and Relationships:
{entities_relationships}

######################

Output:
""",

        "compressor_agent_system": """
""",

        "compressor_agent_user": """
""",

    }

    LEGAL = {

    }

    def __init__(self):
        self.prompts = {
            "chatdoctor": self.CHATDOCTOR,
            "legal": self.LEGAL
        }

    def get_prompt(self, domain: str, prompt: str):
        if domain == "chatdoctor" or domain == "legal":
            return self.prompts[domain][prompt]
        return "prompts not found"

@singleton
class Router:
    knowledge_graph_inst: BaseGraphStorage
    encrypt_chunks_db: BaseKVStorage[EncryptChunkSchema]
    encrypt_entities_db: BaseKVStorage[list[EncryptEntitySchema]]
    encrypt_relationships_db: BaseKVStorage[list[EncryptRelationshipSchema]]

    def __init__(self, domain:str = "chatdoctor", 
                 model_name: str = "gpt-4o", 
                 ip: str = "", 
                 base_url: str = "https://api.onechats.cn/v1", 
                 proxy: str = "http://127.0.0.1:7890", 
                 working_dir: str = "", 
                 entity_types: List[str] = list()):
        self.is_construct = False
        self.domain = domain

        if os.environ.get("MODEL") is not None:
            self.model_name = os.environ["MODEL"]
        else:
            self.model_name = model_name
        
        self.ip = os.environ.get("PROXY_IP", "")
        self.proxy = proxy if ip == "" else f"http://{self.ip}:7890"

        if os.environ.get("BASE_URL") is not None:
            self.base_url = os.environ["BASE_URL"]
        else:
            self.base_url = base_url

        self.working_dir = working_dir
        self.entity_types = entity_types
        self.prompts: PROMPTS = PROMPTS()

    async def construct(self):
        if self.construct is True:
            print("Router is already constructed.")
            return
        self.router = await self.construct_graph()
        self.is_construct = True

    async def invoke(self, query: str, input_data: str, options: List[str]):
        if self.is_construct is False:
            raise Exception("Router is not constructed yet.")
        state = State(query=query, input_data=input_data)
        config = RouterConfig(options=options, entity_types=self.entity_types)
        response = await self.router.ainvoke(state, config=config)
        result = entities_relations_dict_to_csv_text(response.get("entities"), response.get("relations"))
        return result

    def get_llm(self, model_name: str) -> ChatOpenAI:
        if model_name == "gpt-4o":
            filter_llm = ChatOpenAI(model=model_name, 
                            api_key=os.environ["OPENAI_API_KEY"],
                            base_url=self.base_url,
                            openai_proxy=self.proxy)
        elif model_name == "deepseek-chat":
            filter_llm = ChatOpenAI(model=model_name,
                            api_key=os.environ["DEEPSEEK_API_KEY"],
                            base_url=self.base_url,
                            openai_proxy=self.proxy)
        return filter_llm
    
    def get_agent(self, agent_name: str):
        if agent_name == "filter":
            filter_agent_prompt = ChatPromptTemplate.from_messages([("system", self.prompts.get_prompt(self.domain, "filter_agent_system")),
                                                                    ("user", self.prompts.get_prompt(self.domain, "filter_agent_user"))])
            filter_llm = self.get_llm(self.model_name)
            filter = filter_agent_prompt | filter_llm | StrOutputParser()
            return filter
        elif agent_name == "compressor":
            compressor_agent_prompt = ChatPromptTemplate.from_messages([("system", self.prompts.get_prompt(self.domain, "compressor_agent_system")),
                                                                    ("user", self.prompts.get_prompt(self.domain, "compressor_agent_user"))])
            compressor_llm = self.get_llm(self.model_name)
            compressor = compressor_agent_prompt | compressor_llm | StrOutputParser()
            return compressor
        elif agent_name == "query_analysis":
            query_analysis_prompt = ChatPromptTemplate.from_messages([("user", self.prompts.get_prompt(self.domain, "query_analysis"))])
            query_analysis_llm = self.get_llm(self.model_name)
            query_analysis = query_analysis_prompt | query_analysis_llm | StrOutputParser()
            return query_analysis
        elif agent_name == "rerank":
            rerank = CohereRerank(cohere_api_key=os.environ['COHERE_API_KEY'],
                                  model="rerank-v3.5",
                                  top_n=10)
            return rerank

    
    # Nodes
    def data_preprocess(self, state: State, config: RunnableConfig):
        input_data = state["input_data"]
        query = state["query"]
        entities, relations = parse_csv_text_to_list(input_data)
        return {"query": query, "entities": entities, "relations": relations, "input_data": input_data}

    def rerank(self, state: State, config: RunnableConfig):
        if "rerank" not in config['configurable']['options']:
            return state
        query = state["query"]
        entities = state["entities"]
        relations = state["relations"]
        entities_desc = [entity["description"] for entity in entities]
        relations_desc = [relation["description"] for relation in relations]
        rerank_agent = self.get_agent("rerank")
        entities_rel = rerank_agent.rerank(query=query,
                            documents=entities_desc)
        relations_rel = rerank_agent.rerank(query=query,
                            documents=relations_desc)
        entities = [{"id": entities[entity_rel["index"]]["id"], 
                     "entity": entities[entity_rel["index"]]["entity"], 
                     "type": entities[entity_rel["index"]]["type"], 
                     "description": entities[entity_rel["index"]]["description"], 
                     "rank": entities[entity_rel["index"]]["rank"]} 
                     for entity_rel in entities_rel]
        relations = [{"id": relations[relation_rel["index"]]["id"], 
                      "source": relations[relation_rel["index"]]["source"], 
                      "target": relations[relation_rel["index"]]["target"], 
                      "description": relations[relation_rel["index"]]["description"], 
                      "keywords": relations[relation_rel["index"]]["keywords"], 
                      "weight": relations[relation_rel["index"]]["weight"], 
                      "rank": relations[relation_rel["index"]]["rank"]} 
                      for relation_rel in relations_rel]
        return {"query": query, "entities": entities, "relations": relations}

    def filt(self, state: State, config: RunnableConfig):
        if "filt" not in config['configurable']['options']:
            return state
        query = state["query"]
        filter = self.get_agent("filter")
        input_data = entities_relations_dict_to_csv_text(state["entities"], state["relations"])
        response = filter.invoke({"query": query, "entities_relationships": input_data})
        entities, relations = parse_csv_text_to_list(response)
        return {"query": query, "entities": entities, "relations": relations}
    
    async def synthetic(self, state: State, config: RunnableConfig):
        if "synthetic" not in config['configurable']['options']:
            return state
        query = state["query"]
        entities = state["entities"]
        relations = state["relations"]
        syn_entities = []
        syn_relations = []
        query_analysis = self.get_agent("query_analysis")
        query_analysis_response = await query_analysis.ainvoke({"query": query, "entity_types": ",".join(self.entity_types)})
        query_analysis_data = question_analysis_response_to_dict(query_analysis_response)

        for i, entity in enumerate(entities):
            entity_type = entity.get("type", "UNKNOWN")
            encrypt_flag = True
            if query_analysis_data is not None and entity_type in query_analysis_data and query_analysis_data[entity_type][entity_type] == 1:
                encrypt_entity = await self.encrypt_entities_db.get_by_id(entity["entity"])
                if encrypt_entity is not None:
                    encrypt_flag = False
                    for e in encrypt_entity:
                        syn_entities.append({
                            "id": i,
                            "entity": e["encrypt_name"],
                            "type": entity_type,
                            "description": e.get("encrypt_description", "UNKNOWN"),
                            "rank": entity["rank"],
                        })
            if encrypt_flag:
                syn_entities.append({
                    "id": i,
                    "entity": entity["entity"],
                    "type": entity_type,
                    "description": entity.get("description", "UNKNOWN"),
                    "rank": entity["rank"],
                })

        for i, relation in enumerate(relations):
            source = await self.knowledge_graph_inst.get_node(relation["source"])
            target = await self.knowledge_graph_inst.get_node(relation["target"])
            if source is None or target is None:
                continue
            src_type = source.get("entity_type", "UNKNOWN")
            tgt_type = target.get("entity_type", "UNKNOWN")

            encrypt_flag = True
            if query_analysis_data is not None and src_type in query_analysis_data and tgt_type in query_analysis_data and query_analysis_data[src_type][tgt_type] == 1:
                relation_key = tuple_to_str((relation["source"], relation["target"])) 
                encrypt_relation = await self.encrypt_relationships_db.get_by_id(relation_key)
                if encrypt_relation is not None:
                    encrypt_flag = False
                    for r in encrypt_relation:
                        syn_relations.append({                            
                            "id": i,
                            "source": r["encrypt_src_id"],
                            "target": r["encrypt_tgt_id"],
                            "description": r["encrypt_description"],
                            "keywords": r["encrypt_keywords"],
                            "weight": relation["weight"],
                            "rank": relation["rank"],
                        })
            if encrypt_flag:
                syn_relations.append({
                    "id": i,
                    "source": relation["source"],
                    "target": relation["target"],
                    "description": relation["description"],
                    "keywords": relation["keywords"],
                    "weight": relation["weight"],
                    "rank": relation["rank"],
                })
        return {"query": query, "entities": syn_entities, "relations": syn_relations}


    def compress(self, state: State, config: RunnableConfig):
        if "compress" not in config['configurable']['options']:
            return state
        entities = state["entities"]
        relations = state["relations"]
        compressor = Router.get_agent("compressor")
        # Implement compressor agent
        input_data = entities_relations_dict_to_csv_text(entities, relations)
        response = compressor.invoke({"query": query, "entities_relationships": input_data})
        return {"query": state["query"], "entities": entities, "relations": relations, "retrieved_context": response}

    # Edges
    def option_choose(state: State, config: RunnableConfig):
        # not in use
        order = ['filt', 'compress', 'rerank', 'synthetic', 'end']
        options = config["configurable"]["options"]
        pre_node = config["metadata"]["langgraph_node"]
        
            
    async def construct_graph(self):
        workflow = StateGraph(State, config_schema=RouterConfig)
        workflow.add_node("preprocess", self.data_preprocess)
        workflow.add_node("filt", self.filt)
        workflow.add_node("compress", self.compress)
        workflow.add_node("rerank", self.rerank)
        workflow.add_node("synthetic", self.synthetic)
        workflow.add_edge(START, "preprocess")
        workflow.add_edge("preprocess", "rerank")
        workflow.add_edge("rerank", "filt")
        workflow.add_edge("filt", "synthetic")
        workflow.add_edge("synthetic", "compress")
        workflow.add_edge("compress", END)
        return workflow.compile()

def parse_csv_text_to_list(context):
    def split_csv_line(line):
        return re.split(r',\s*(?=(?:[^"]*"[^"]*")*[^"]*$)', line)
    re_result = re.findall(r'\`\`\`csv\s+([\s\S]*?)\s+\`\`\`', context)
    if len(re_result) != 2:
        return None
    entities = re_result[0]
    relations = re_result[1]
    entities = [split_csv_line(entity) for entity in entities.split("\n")]
    relations = [split_csv_line(relation) for relation in relations.split("\n")]
    entities_list = []
    relations_list = []
    for i, entity in enumerate(entities):
        if len(entity) == 5 and i:
            entities_list.append({"id": i, "entity": entity[1], "type": entity[2], "description": entity[3], "rank": entity[4]})
    for i, relation in enumerate(relations):
        if len(relation) == 7 and i:
            relations_list.append({"id": i, "source": relation[1], "target": relation[2], "description": relation[3], "keywords": relation[4], "weight": relation[5], "rank": relation[6]})
        
    return entities_list, relations_list

def question_analysis_response_to_dict(csv_data: str) -> dict:
    try:
        lines = csv_data.strip().split('\n')
        if not lines:
            return None
        header = [f'"{h}"' for h in lines[0].upper().split(',')]
        num_columns = len(header)
        for line in lines[1:]:
            row = line.split(',')
            if len(row) != num_columns:
                return None
        result = {}
        for idx, line in enumerate(lines[1:]):
            row = line.split(',')
            if idx >= len(header):
                return None
            row_key = header[idx]
            value_dict = {}
            for col, val in zip(header, row):
                value_dict[col] = int(val)
            result[row_key] = value_dict
        return result
    except Exception:
        return None

def tuple_to_str(tuple_data: tuple) -> str:
    return str(tuple_data)

def list_of_dict_to_csv(data: list[dict]) -> str:
    title = ",\t".join([f'{key}' for key in data[0].keys()])
    content = "\n".join([",\t".join([str(data_dd) for data_dd in data_d.values()]) for data_d in data])
    return f"{title}\n{content}"

def entities_relations_dict_to_csv_text(entities: List[Dict], relations: List[Dict]) -> str:
    entities_csv = list_of_dict_to_csv(entities)
    relations_csv = list_of_dict_to_csv(relations)
    return f"-----Entities-----\n```csv\n{entities_csv}\n```\n-----Relationships-----\n```csv\n{relations_csv}\n```"

if __name__ == "__main__":
    test_data = """-----Entities-----
```csv
id,     entity, type,   description,    rank
0,      "DERMATOLOGIST APPOINTMENT",    "MEDICAL PLAN", "The doctor recommends scheduling an appointment with a dermatologist for a proper diagnosis.", 1
1,      "PROPER DIAGNOSIS",     "MEDICAL PLAN", "A proper diagnosis of the patient's condition is needed to tailor the treatment and address the underlying issue.",    0
3,      "SENSITIVE SKIN",       "HEALTH CONDITION",     "A condition attributed by the pediatrician as the reason for pimples, characterized by a reaction to environmental factors.",  2
5,      "EYELID INFECTION",     "DISEASES",     "A potential diagnosis given by the doctor, suggesting that the bump may be an infection related to the eyelid.",       2
7,      "ACNE-LIKE RASH",       "SYMPTOMS",     "The cheek area around Mike's tooth has developed a rash resembling acne.",     2
10,     "PUS DRAINAGE", "MEDICAL PLAN", "A potential part of the treatment plan if the infection is confirmed, to relieve the persistent inflammation in the bump.",    1
11,     "PEMPHIGUS",    "DISEASES",     "A potential skin condition mentioned by the doctor that could be causing the patient's symptoms and requires dermatologist examination for proper diagnosis.", 1
12,     "PEMPHIGOID",   "DISEASES",     "Another potential skin condition suggested by the doctor that could explain the patient's symptoms, needing dermatologist examination for confirmation.",      1
14,     "CONTACT DERMATITIS",   "HEALTH CONDITION",     "Ivory's rash diagnosed as contact dermatitis, treated with zinc oxide cream.", 1
17,     "MILD SOAP, AVOIDING HARSH SCRUBS, MOISTURIZING",       "LIFESTYLE",    "Lifestyle alterations recommended by the doctor to potentially relieve symptoms and prevent aggravation of the patient's rash.",       1
18,     "ECZEMA",       "DISEASES",     "A skin condition initially suspected by the mother as the cause of Ivory's rash, later diagnosed as contact dermatitis.",      0
```
-----Relationships-----
```csv
id,     source, target, description,    keywords,       weight, rank
2,      "INFECTION",    "PUS DRAINAGE", "If the bump is infected, pus drainage might be necessary as part of the medical plan to treat the condition.", "treatment, medical intervention",      9.0,    18
3,      "PEDIATRICIAN", "SENSITIVE SKIN",       "The pediatrician identified the daughter's skin issue as sensitive skin and advised no immediate medication.", "medical diagnosis, expert opinion",    9.0,    18
17,     "CONTACT DERMATITIS",   "RASH", "The rash is diagnosed as contact dermatitis, a specific health condition.",    "diagnosis, medical assessment",        10.0,   6
22,     "PIMPLES",      "SENSITIVE SKIN",       "Sensitive skin is thought to be the underlying cause of the daughter's pimples by her pediatrician.",  "cause-effect, skin condition", 8.0,    5
23,     "PEMPHIGOID",   "PERSISTENT RED BUMPY RASH",    "The rash and symptoms described also match the characteristics of pemphigoid, another potential diagnosis.",   "potential diagnosis, skin condition",  8.0,    4
24,     "PEMPHIGUS",    "PERSISTENT RED BUMPY RASH",    "The rash and symptoms described match the characteristics of the disease pemphigus, as suggested by the doctor.",      "potential diagnosis, skin condition",  8.0,    4
26,     "MILD SOAP, AVOIDING HARSH SCRUBS, MOISTURIZING",       "PERSISTENT RED BUMPY RASH",    "Lifestyle changes suggested to Sarah to help manage the symptoms of her partner's rash.",      "symptom management, lifestyle adjustment",     7.0,    4
29,     "ACNE-LIKE RASH",       "CHEEK BITE",   "The rash Mike experiences may be due to a cheek bite caused by the wisdom tooth.",     "possible cause",       6.0,    3
30,     "ACNE-LIKE RASH",       "CANDIDIASIS",  "Candidiasis might be causing the rash symptoms on Mike's cheek.",      "possible diagnosis",   5.0,    3
```
"""
    router = Router(entity_types=["health condition", "person", "diseases", "family medical history", "lifestyle", "medications", "medical plan", "symptoms"], ip="172.19.184.209")
    query = "if i was diagnosed with acne, what should i do?"
    response = router.invoke(query=query, input_data=test_data, options=["filt"])
    print(response.get("entities"))
    print(response.get("relations"))