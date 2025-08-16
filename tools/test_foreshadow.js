const rt = require('../runtime');
rt.state.ui.gm_style = process.env.GM_STYLE || 'verbose';
rt.state.scene.foreshadows = 0;
rt.assert_foreshadow(2);
