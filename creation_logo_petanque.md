# Création du fichier `logo_petanque.png`

## Outil de génération

Le fichier est généré par l'IA générative d'images **venice.ai** :

- **URL** : https://venice.ai/studio/image
- **Modèle** : Grok Imagine

## Prompt utilisé

```
Trois boules de pétanque réalistes sur fond transparent :
1ère boule : acier brossé avec gravures géométriques (losanges).
2ème boule : bronze/cuivre avec numéros gravés (3 et 8).
3ème boule : noir mat avec symboles de trèfle gravés.
1 petit cochonet peint en orange fluo mat.
Les boules et le cochonet reposent sur un sol sablonneux.
L'arrière plan est découpé en forme d'ellipse englobant le sol, le cochonet et les boules.
Complètement blanc en dehors de l'ellipse.
Les boules et le cochonet occupent un maximum de la place dans l'ellipse.
La largeur de l'ellipse occupe toute la largeur de l'image.
L'ellipse est centrée dans l'image finale.
Ombres réalistes sous les boules, finition professionnelle, rendu 3D, photographie réaliste.
```

## Post-traitement

La bordure blanche autour de l'ellipse est rendue transparente avec **GIMP** :

1. Ouvrir le fichier dans GIMP.
2. Sélectionner le blanc avec la **baguette magique**.
3. `Calque` → **`Ajouter un canal alpha`**.
4. Appuyer sur **Suppr** pour effacer le blanc sélectionné.
5. **Écraser le fichier original** : `Fichier` → `Écraser`.
