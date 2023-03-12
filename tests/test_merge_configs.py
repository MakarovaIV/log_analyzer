import unittest
from log_analyzer import merge_configs

test_default_config = {
    "INT_PARAM": 10,
    "STR_PARAM": "str_default",
    "PARAM_ONLY_IN_DFAULT": 'test_default'
}

external_config = {
    "INT_PARAM": 20,
    "STR_PARAM": "str_ext",
    "EXCEED_PARAM": 100,
}


class MergeConfigsTest(unittest.TestCase):
    def test_merge_two_configs(self):
        merged_cfg = merge_configs(test_default_config, external_config)
        self.assertEqual(external_config["INT_PARAM"], merged_cfg["INT_PARAM"])
        self.assertEqual(external_config["STR_PARAM"], merged_cfg["STR_PARAM"])
        self.assertEqual(test_default_config["PARAM_ONLY_IN_DFAULT"], merged_cfg["PARAM_ONLY_IN_DFAULT"])
        self.assertNotIn("EXCEED_PARAM", merged_cfg)

    def test_without_ext_config(self):
        merged_cfg = merge_configs(test_default_config, None)
        self.assertEqual(test_default_config["INT_PARAM"], merged_cfg["INT_PARAM"])

    def test_without_default_config(self):
        merge_configs(None, external_config)
        self.assertRaises(Exception)
