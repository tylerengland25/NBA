from update_shooting import update as update_scrape_shooting
from update_scoring import update as update_scrape_scoring
from update_game_details import update as update_game_details
from update_game_totals import update as update_game_totals
from odds import update_odds
from schedule import update_schedule


def update_all():
    # update_schedule(2022)
    # update_scrape_shooting()
    update_scrape_scoring()
    # update_game_details()
    # update_game_totals()
    # update_odds()


if __name__ == '__main__':
    update_all()
