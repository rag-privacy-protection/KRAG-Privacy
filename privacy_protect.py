import os
from privacy import LightRAG, QueryParam
from privacy.llm import openai_complete_if_cache, openai_embedding
from privacy.utils import EmbeddingFunc
from privacy.prompt import PROMPTS
import json
from privacy.llm import hf_embedding
from transformers import AutoModel, AutoTokenizer
import pandas as pd
import numpy as np
from tqdm import tqdm
import time

async def llm_model_func(
    prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    return await openai_complete_if_cache(
        # deepseek-chat
        "deepseek-chat",
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com",

        # # gpt-4o
        # "gpt-4o",
        # api_key=os.environ["OPENAI_API_KEY"],
        # base_url="https://api.onechats.cn/v1",

        prompt=prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        **kwargs
    )

async def embedding_func(texts: list[str]) -> np.ndarray:
    return await openai_embedding(
        texts,
        api_key="sk-g8T5VApORkXOP9K554Ac88Ca3eAe4e8f819c9fD8C2Cb7293",
        base_url="https://api.onechats.cn/v1"
    )

def insert_data(rag: LightRAG, dataset: str):
    timings = []
    if dataset == "chatdoctor":
        with open("./data/chatdoctor.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for i in tqdm(range(len(data))):
                pair = data[i]
                input_entry = pair[0]
                input_text = input_entry.replace("input: ", "").replace("output: ", "")
                start_time = time.time()
                rag.insert(input_text)
                end_time = time.time()
                timings.append([i, end_time - start_time])
                timings_df = pd.DataFrame(timings, columns=["id", "time_taken"])
                timings_df.to_csv("./data/insert_timings.csv", index=False)
    elif dataset == "chatdoctor-plus":
        data = pd.read_csv('./data/chatdoctor-plus.csv')
        for index in tqdm(range(len(data))):
            try:
                start_time = time.time()
                rag.insert(data.at[index, 'text'])
                end_time = time.time()
                timings.append([index, end_time - start_time])
            except Exception as e:
                time.sleep(60)
                start_time = time.time()
                rag.insert(data.at[index, 'text'])
                end_time = time.time()
                timings.append([index, end_time - start_time])
            timings_df = pd.DataFrame(timings, columns=["id", "time_taken"])
            timings_df.to_csv("./data/insert_timings.csv", index=False)
    print("insert done")

def query_and_save(rag: LightRAG, prompt_df: pd.DataFrame, response_df: pd.DataFrame, index: int):
    response = rag.query(prompt_df.at[index, 'prompt'], param=QueryParam(mode="local", encrypt_mode=True, top_k=20))
    response_df.at[index, 'response'] = response

def privacy_evaluation(rag: LightRAG, prompt_path: str, response_path: str):
    prompt_df = pd.read_csv(prompt_path)
    response_df = pd.read_csv(response_path)
    save_step = 10

    for index in tqdm(range(len(prompt_df))):
        if not pd.isna(response_df.at[index, 'response']):
            print(f"skip Num.{index} privacy evaluation prompt.")
            continue
        if index % save_step == 0:
            response_df.to_csv(response_path, index=False)
        query_and_save(rag, prompt_df, response_df, index)
    
    response_df.to_csv(response_path, index=False)
    print("privacy evaluation done")

def utility_evaluation(rag: LightRAG, ragas_tests_path: str):
    ragas_tests = pd.read_csv(ragas_tests_path)
    save_step = 10

    for index in tqdm(range(len(ragas_tests))):
        if not pd.isna(ragas_tests.at[index, 'response']) and not pd.isna(ragas_tests.at[index, 'retrieved_contexts']):
            print(f"skip Num.{index} utility evaluation prompt.")
            continue
        if index % save_step == 0:
            ragas_tests.to_csv(ragas_tests_path, index=False)
        input = ragas_tests.at[index, 'user_input']
        response, retrieved_contexts = rag.query(input, param=QueryParam(mode="local", encrypt_mode=True, top_k=20, return_context=True))
        ragas_tests.at[index, 'response'] = response
        ragas_tests.at[index, 'retrieved_contexts'] = retrieved_contexts

    ragas_tests.to_csv(ragas_tests_path, index=False)
    print("utility evaluation done")

def query_time(rag: LightRAG):
    data = pd.read_csv("./data/query_time.csv")
    for index in tqdm(range(96, len(data))):
        start_time = time.time()
        response = rag.query(data.at[index, 'prompt'], param=QueryParam(mode="local", encrypt_mode=True, top_k=20, privacy_options=['rerank', 'filt', 'synthetic']))
        end_time = time.time()
        data.at[index, 'response'] = response
        data.at[index, 'time'] = end_time - start_time
        data.to_csv("./data/query_time.csv", index=False)
    
def retriver_chunks(rag: LightRAG, top_k: int):
    data = pd.read_csv("./data/query_time.csv")
    retrieved_chunks = []
    for index in tqdm(range(len(data))):
        chunks = rag.retrieve(query=data.at[index, 'prompt'], top_k=top_k)
        docs_num = len(chunks)
        for chunk in chunks:
            if chunk['id'] in retrieved_chunks:
                docs_num -= 1
            retrieved_chunks.append(chunk['id'])
        data.at[index, 'new_docs'] = docs_num
        data.to_csv("./data/query_time.csv", index=False)
    return chunks

if __name__ == "__main__":
    WORKING_DIR = "./data/chatdoctor-plus-4o"

    if not os.path.exists(WORKING_DIR):
        os.mkdir(WORKING_DIR)

    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=llm_model_func,
        encrypt_llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=1536,
            max_token_size=2048,
            func=embedding_func
        )
    )

    # insert data
    # insert_data(rag, "chatdoctor-plus")

    # encrypt data
    # rag.encrypt()
    # print("encrypt done")

    # evaluation
    # privacy_evaluation(rag, "./output/legal_default_new/prompt_legal-plus.csv", "./output/legal_default_new/response_template_legal-plus.csv")
    # utility_evaluation(rag, "./output/ragas_question_legal_plus.csv")

    # test
    # response = rag.query("If I was diagnosed with pituitary tumor, what should I do?", param=QueryParam(mode="local", encrypt_mode=True, top_k=20, privacy_options=['rerank', 'filt', 'synthetic'], only_need_context=True))
    # print(response)
    # query_time(rag)
    retriver_chunks(rag, 5)