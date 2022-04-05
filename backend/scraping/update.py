from update_shooting import main as scrape_shooting
from update_scoring import main as scrape_scoring
from update_game_details import main as scrape_game_details
from odds import update_odds


def update_all():
    scrape_shooting()
    scrape_scoring()
    scrape_game_details()
    update_odds()


if __name__ == '__main__':
    update_all()
