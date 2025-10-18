const assert = require('assert');
const rt = require('../runtime');

const commands = ['!helper delay', '!helper comms', '!helper boss'];

commands.forEach((command) => {
  const response = rt.on_command(command);
  assert.strictEqual(typeof response, 'string', `${command} liefert keinen String`);
  assert(response.trim().length > 0, `${command} liefert einen leeren Text`);
});

console.log('helper-commands-ok');
