import unittest
import ai_chatbot.main

class TestMain(unittest.TestCase):
    def test_rand(self):
        self.assertEqual(len(main.id_generator(6)), 6)
        self.assertEqual(len(main.id_generator(12)), 12)
        self.assertEqual(len(main.id_generator(18)), 18)

if __name__ == '__main__':
    unittest.main()

