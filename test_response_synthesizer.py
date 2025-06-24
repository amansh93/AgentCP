import unittest
import pandas as pd
from unittest.mock import patch
from agent.response_synthesizer import ResponseSynthesizer
from agent.workspace import AgentWorkspace

class TestResponseSynthesizer(unittest.TestCase):

    def setUp(self):
        self.synthesizer = ResponseSynthesizer()
        self.workspace = AgentWorkspace()

    @patch('openai.resources.chat.completions.Completions.create')
    def test_synthesize_table(self, mock_create):
        # Mock the LLM response
        mock_create.return_value.choices[0].message.content = "This is a test table."
        
        # Create a sample dataframe
        df = pd.DataFrame({'client_name': ['A', 'B'], 'revenue': [100, 200]})
        self.workspace.add_df("test_df", df)
        
        # Synthesize the response
        result = self.synthesizer.synthesize("Show revenues", self.workspace)
        
        # Get the prompt passed to the LLM
        sent_prompt = mock_create.call_args[1]['messages'][1]['content']
        
        self.assertIn("client_name", sent_prompt)
        self.assertIn("revenue", sent_prompt)
        self.assertEqual(result, "This is a test table.")

    @patch('openai.resources.chat.completions.Completions.create')
    def test_synthesize_plot(self, mock_create):
        # Mock the LLM response
        mock_create.return_value.choices[0].message.content = "This is a test plot."
        
        # Create a dataframe with a plot path
        df = pd.DataFrame([{'plot_path': '/static/plots/test.png'}])
        self.workspace.add_df("plot_df", df)
        
        result = self.synthesizer.synthesize("Plot revenues", self.workspace)
        sent_prompt = mock_create.call_args[1]['messages'][1]['content']
        
        self.assertIn('<img src="/static/plots/test.png" alt="Financial Plot" style="max-width: 800px; width: 100%; height: auto;">', sent_prompt)
        self.assertEqual(result, "This is a test plot.")

    @patch('openai.resources.chat.completions.Completions.create')
    def test_synthesize_client_links(self, mock_create):
        # Mock the LLM response
        mock_create.return_value.choices[0].message.content = "This is a test with client links."
        
        # Create a dataframe with client info
        df = pd.DataFrame({'client_name': ['Test Client'], 'client_id': ['test_id']})
        self.workspace.add_df("client_df", df)
        
        result = self.synthesizer.synthesize("Show client info", self.workspace)
        sent_prompt = mock_create.call_args[1]['messages'][1]['content']
        
        self.assertIn("[Test Client](https://my-internal-platform.com/clients/test_id)", sent_prompt)
        self.assertEqual(result, "This is a test with client links.")

if __name__ == '__main__':
    unittest.main() 