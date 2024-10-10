
class GPTPrompts():
    def __init__(self) -> None:


        self.summarize_prompt: str = """
            You are a news editor. Summarize the article in no more than 50 words, 
            maintaining the same tone and writing style. Ensure the summary captures 
            the key facts, figures, and data from the article, and focuses on the most 
            Ensure to return the exact number of articles you are given.
            critical information, like factual numbers/percentages. Return only the summarized text prefixed with 'Summary 
            for Article X:', where X is the article number.
            <<START>>
            """

        # self.flagger_prompt:str = """
        #     Your only task is to analyze the provided text and determine if the content appears to be paywalled, privacy blocked, or not an article. 
        #     Respond with a comma-separated list of responses for each article in the order they are presented, using "yes" if the text seems paywalled, 
        #     blocked or not an article, and "no" if it is not. 
        #     Each article will be decorated with the tag "<<END>>" to indicate its end.
        #     Please format your response as follows:
        #     yes, no, yes, no  # Example format for 4 articles

        #     """
        self.flagger_prompt:str = """
            Your task is to evaluate the provided text and determine whether the content appears to be paywalled, privacy-blocked, a cookies policy, 
            or not a proper article. For each article, respond with "yes" if the text even slightly suggests it might be paywalled, blocked, a cookies policy,
            or not a legitimate article. Respond with "no" if it is clearly accessible and appears to be a proper article. Articles will be marked with the tag
            "<<END>>" to indicate their conclusion.

            Please format your response as a comma-separated list of "yes" or "no" for each article in the order presented. Example: yes, no, yes, no.

            """
        
            # Ensure to return the exact number of responses as the number of articles given.


        # 1. Your sole role.
        # 2. Writing style
        # 3. Facts and figures
        # 4. Return the exact number you are passed.