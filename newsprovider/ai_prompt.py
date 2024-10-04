
class GPTPrompts():
    def __init__(self) -> None:


        self.summarize_prompt: str = """
            You are a news editor. Summarize the article in no more than 50 words, 
            maintaining the same tone and writing style. Ensure the summary captures 
            the key facts, figures, and data from the article, and focuses on the most 
            critical information, like factual numbers/percentages. Return only the summarized text prefixed with 'Summary 
            for Article X:', where X is the article number.
            <<START>>
            """

        self.flagger_prompt:str = """
            Your only task is to analyze the provided text and determine if the content appears to be paywalled, privacy blocked, or not an article. 
            Respond with a comma-separated list of responses for each article in the order they are presented, using "yes" if the text seems paywalled, 
            blocked or not an article, and "no" if it is not. 
            Each article will be decorated with the tag "<<END>>" to indicate its end.
            Please format your response as follows:
            yes, no, yes, no  # Example format for 4 articles

            """