import unittest
import lambda_function

class TestHandlerCase(unittest.TestCase):

    def test_response(self):
        response = lambda_function.lambda_handler(None, None)
        self.assertIn("HelloWorld", response['body'])

if __name__ == '__main__':
    unittest.main()