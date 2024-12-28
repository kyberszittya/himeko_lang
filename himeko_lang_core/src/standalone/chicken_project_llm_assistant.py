import sys

from openai import OpenAI


class GetCameraFromWebshops(object):

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)

    # Function to generate code based on meta-element and description
    def get_recommendations(self, description: str):
        """
        Generate code based on a meta-element description and user description.

        Parameters:
        - meta_description (str): High-level description of the function or module.
        - description (str): Additional details or specific requirements.
        - framework (str): The language or framework for code generation (e.g., 'pytorch', 'tensorflow', 'python').

        Returns:
        - str: Generated code from OpenAI API.
        """

        # Construct prompt with meta-description and user description
        prompt = (f"Description: {description}\n\n"
                  f"Execute query object!\n\n"
                  f"Result:\n")

        try:
            # Call OpenAI API with the prompt
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a sales assistant giving a search query, based on the description."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract code from the response
            generated_code = response.choices[0].message.content.strip()
            return generated_code

        except Exception as e:
            return f"An error occurred: {str(e)}"


def main():
    # Example usage
    description_file = "D:/Hakiko/himeko_ws/hypergraph_dataflow_ws/himeko_lang/himeko_lang_core/examples/agriculture/chicken_camera.himeko"
    description = ''.join(open(description_file).readlines())
    ai_key = open("openai_api.key").read().strip()
    camera_from_webshops = GetCameraFromWebshops(ai_key)
    generated_code = camera_from_webshops.get_recommendations(description)
    print(generated_code)


if __name__=="__main__":
    main()
