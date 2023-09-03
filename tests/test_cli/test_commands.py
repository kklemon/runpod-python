'''
RunPod | Tests | CLI | Commands
'''

import unittest
from unittest.mock import patch
from click.testing import CliRunner

from runpod.cli.entry import runpod_cli

class TestCommands(unittest.TestCase):
    ''' A collection of tests for the CLI commands. '''

    def setUp(self):
        self.runner = CliRunner()

    def test_config_wizard(self):
        ''' Tests the config command. '''
        with patch('click.echo') as mock_echo, \
            patch('runpod.cli.config.commands.set_credentials') as mock_set_credentials, \
            patch('runpod.cli.config.commands.check_credentials') as mock_check_credentials, \
            patch('click.confirm', return_value=True) as mock_confirm, \
            patch('click.prompt', return_value='KEY') as mock_prompt:

            # Assuming credentials aren't set (doesn't prompt for overwrite)
            mock_check_credentials.return_value = (False, None)

            # Successful Call with Direct Key
            result = self.runner.invoke(runpod_cli, ['config', '--profile', 'test', 'KEY'])
            assert result.exit_code == 0
            mock_set_credentials.assert_called_with('KEY', 'test')
            assert mock_echo.call_count == 1

            # Successful Call with Prompted Key (since direct key isn't provided)
            result = self.runner.invoke(runpod_cli, ['config', '--profile', 'test'])
            assert result.exit_code == 0
            mock_set_credentials.assert_called_with('KEY', 'test')
            mock_prompt.assert_called_with('API Key', hide_input=False, confirmation_prompt=True)

            # Simulating existing credentials, prompting for overwrite
            mock_check_credentials.return_value = (True, None)
            result = self.runner.invoke(runpod_cli, ['config', '--profile', 'test'])
            mock_confirm.assert_called_with(
                'Credentials already set for profile: test. Overwrite?', abort=True)

            # Unsuccessful Call
            mock_set_credentials.side_effect = ValueError()
            result = self.runner.invoke(runpod_cli, ['config', '--profile', 'test', 'KEY'])
            assert result.exit_code == 1

    def test_store_api_key(self):
        ''' Tests the store_api_key command. '''
        with patch('click.echo') as mock_echo, \
             patch('runpod.cli.config.functions.set_credentials') as mock_set_credentials:

            # Successful Call
            result = self.runner.invoke(runpod_cli, ['store_api_key', '--profile', 'test', 'KEY'])
            assert result.exit_code == 0
            assert mock_set_credentials.called_with('API_KEY_1234', 'test')
            assert mock_echo.call_count == 1

            # Unsuccessful Call
            mock_set_credentials.side_effect = ValueError()
            result = self.runner.invoke(runpod_cli, ['store_api_key', '--profile', 'test', 'KEY'])
            assert result.exit_code == 1

    def test_validate_credentials_file(self):
        ''' Tests the check_creds command. '''
        with patch('click.echo') as mock_echo, \
             patch('runpod.cli.config.commands.check_credentials') as mock_check_credentials:

            # Successful Validation
            mock_check_credentials.return_value = (True, None)
            result = self.runner.invoke(runpod_cli, ['check_creds', '--profile', 'test_pass'])
            assert mock_check_credentials.called_with('test_pass')
            assert mock_check_credentials.return_value == (True, None)
            assert result.exit_code == 0

            # Unsuccessful Validation
            mock_check_credentials.return_value = (False, 'Error')
            result = self.runner.invoke(runpod_cli, ['check_creds', '--profile', 'test'])
            assert result.exit_code == 1
            assert mock_check_credentials.called_with('test')
            assert mock_echo.call_count == 4
