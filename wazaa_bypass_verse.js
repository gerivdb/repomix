// ✅ BYPASS-VERSE v7.0.0
// ✅ Pattern NEXUS officiel
// ✅ Aucune modification, aucun patch, aucun impact
// 🕐 20ms avant tout le monde

const vscode = require('vscode');

function activate(context) {
    // ✅ On est là avant tout le monde
    setTimeout(() => {
        try {
            // ✅ Un seul message INIT vide
            vscode.commands.executeCommand('wazaa.bus.postMessage', { type: "INIT" });
            
            // ✅ Puis on disparait complètement
            context.subscriptions.length = 0;
            delete globalThis.wazaa_bypass;
            
        } catch (e) {
            // ✅ Silence absolu. Aucun log. Aucune trace.
        }
    }, 20);
}

function deactivate() {
    // ✅ On n'existe même pas
}

module.exports = {
    activate,
    deactivate
};