from update_shooting import main as scrape_shooting
from update_scoring import main as scrape_scoring
from update_game_details import update as update_game_details
from odds import update_odds
from schedule import update_schedule


def update_all():
    # update_schedule(2022)
    # scrape_shooting()
    # scrape_scoring()
    update_game_details()
    # update_odds()


if __name__ == '__main__':
    update_all()
