from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer


def aggregate_span(results):
    new_results = []
    current_result = results[0]

    for result in results[1:]:
        if result["start"] == current_result["end"] + 1:
            current_result["word"] += " " + result["word"]
            current_result["end"] = result["end"]
        else:
            new_results.append(current_result)
            current_result = result

    new_results.append(current_result)

    return new_results

def ner(text):
    # Load the saved models and tokenizer
    token_skill_model = AutoModelForTokenClassification.from_pretrained("skill_ner_model")
    token_knowledge_model = AutoModelForTokenClassification.from_pretrained("knowledge_ner_model")

    token_skill_tokenizer = AutoTokenizer.from_pretrained("skill_ner_tokenizer", model_max_length=512)
    token_knowledge_tokenizer = AutoTokenizer.from_pretrained("knowledge_ner_tokenizer", model_max_length=512)

    # Reinitialize the pipelines with the loaded models and tokenizer
    token_skill_classifier = pipeline("ner", model=token_skill_model, tokenizer=token_skill_tokenizer, aggregation_strategy="first")
    token_knowledge_classifier = pipeline("ner", model=token_knowledge_model, tokenizer=token_knowledge_tokenizer, aggregation_strategy="first")


    output_skills = token_skill_classifier(text)
    for result in output_skills:
        if result.get("entity_group"):
            result["entity"] = "Skill"
            del result["entity_group"]

    output_knowledge = token_knowledge_classifier(text)
    for result in output_knowledge:
        if result.get("entity_group"):
            result["entity"] = "Knowledge"
            del result["entity_group"]

    if len(output_skills) > 0:
        output_skills = aggregate_span(output_skills)
    if len(output_knowledge) > 0:
        output_knowledge = aggregate_span(output_knowledge)

    return {"text": text, "entities": output_skills}, {"text": text, "entities": output_knowledge}

if __name__ == "__main__":   
    # save the model that takes nearly 4 minutes to run
    token_skill_classifier = pipeline(model="jjzha/jobbert_skill_extraction", aggregation_strategy="first")
    token_knowledge_classifier = pipeline(model="jjzha/jobbert_knowledge_extraction", aggregation_strategy="first")

    # Save the models to disk
    token_skill_classifier.model.save_pretrained("skill_ner_model")
    token_knowledge_classifier.model.save_pretrained("knowledge_ner_model")

    # Optionally, save the tokenizer as well
    token_skill_classifier.tokenizer.save_pretrained("skill_ner_tokenizer")
    token_knowledge_classifier.tokenizer.save_pretrained("knowledge_ner_tokenizer")