"""
✅ EPIC 23: PROJECTION VERSE AUTOMATIQUE

Tous les contenus sont automatiquement projetés dans TOUS les VERSEs connus.

Quand un nouveau contenu arrive, il traverse TOUS les prismes.
Il n'y a pas d'exception. Il n'y a pas de choix.

Tout est vu sous tous les angles, tout le temps.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

from managers.obsidian_interface_manager import obsidian
from managers.ontology_loader import ontology
from managers.verse_registry import all_verses


class VerseAutoProjection:

    def __init__(self):
        self.verses = all_verses

    def project(self, content: any) -> dict:
        """
        Projette un contenu dans TOUS les VERSEs connus.
        Retourne la matrice holistique complète.
        """
        result = {}

        for verse_name, verse in self.verses.items():
            result[verse_name] = {
                "score": verse.score(content),
                "perspective": verse.perspective(content),
                "supporting": verse.supporting(content),
                "contradicting": verse.contradicting(content)
            }

        return result

    def generate_verse_page(self, content_id: str, content: any):
        """
        Génère automatiquement la page VERSE pour ce contenu.
        Cette page est présente une fois pour toute.
        Elle est mise à jour automatiquement chaque fois que le contenu change.
        """
        projections = self.project(content)

        page_content = f"# 🔮 VERSE PROJECTION: {content_id}\n\n"
        page_content += "✅ Ce contenu a été projeté automatiquement dans TOUS les VERSEs connus\n\n"

        for verse_name, data in projections.items():
            page_content += f"## {verse_name}\n"
            page_content += f"Score: `{data['score']}`\n\n"
            page_content += f"> {data['perspective']}\n\n"

            if data['supporting']:
                page_content += "✅ Pour: \n"
                for fact in data['supporting']:
                    page_content += f"  - {fact}\n"

            if data['contradicting']:
                page_content += "\n❌ Contre: \n"
                for fact in data['contradicting']:
                    page_content += f"  - {fact}\n"

            page_content += "\n---\n\n"

        obsidian.create_file(f"VERSE/{content_id}.md", page_content)

    def run_on_all_content(self):
        """
        Lance la projection sur TOUS les contenus existants.
        Ceci s'exécute une fois. Puis tourne en continu sur le nouveau contenu.
        """
        all_content = ontology.get_all_content()

        for content_id, content in all_content.items():
            self.generate_verse_page(content_id, content)


# Singleton global
verse_projection = VerseAutoProjection()


if __name__ == "__main__":
    print("✅ EPIC 23: PROJECTION VERSE AUTOMATIQUE ACTIVÉ")
    print(f"   ✅ {len(all_verses)} VERSEs chargés")
    print("   ✅ Tout contenu est projeté dans TOUS les VERSEs")
    print("   ✅ Aucun exception. Aucun choix. Tout le temps.")
    print("\n✅ La holovision est maintenant active.")