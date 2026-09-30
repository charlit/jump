# QA — jump (local, mobile 375x812) — 2026-09-30

Testé : menu, choix Polux / Rose, contrôle tactile gauche/droite, rebonds, ressorts,
plateformes mobiles et cassantes, défilement infini, score, game over, record (localStorage),
Rejouer, Changer d'animal. Bot automatique 20 s : 160 pts, puis game over correct. 0 erreur console du jeu.

| # | Sévérité | Problème | Statut |
|---|----------|----------|--------|
| 001 | Moyenne | Appui long iOS peut déclencher la loupe / menu contextuel | Corrigé (`-webkit-touch-callout:none`) |

Non testable ici : inclinaison réelle (gyroscope) — à vérifier sur téléphone.
Santé : 90 → 95. "QA found 1 issue, fixed 1, health score 90 → 95."
