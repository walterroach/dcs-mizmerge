import argparse
from copy import deepcopy
from dataclasses import dataclass
from multiprocessing.connection import Client
from pathlib import Path
from typing import Dict, Type, TypedDict, Mapping

import dcs
from dcs.mission import Mission
from dcs.coalition import Coalition
from dcs.countries import country_dict

from mizmerge import pydcs_extensions


def country_id_from_name(name: str) -> int:
    return next((k for k, v in country_dict.items() if v.name == name), -1)


class ClientFlightCollection(TypedDict):
    blue: Mapping[str, list[dcs.unitgroup.FlyingGroup]]
    red: Mapping[str, list[dcs.unitgroup.FlyingGroup]]
    neutrals: Dict[str, list[dcs.unitgroup.FlyingGroup]]


class ClientFlight:
    @staticmethod
    def get_client_flights(miz1: Mission) -> ClientFlightCollection:
        """
        Finds all groups with at least one client unit and returns them as a ClientFlightCollection
        """
        client_flights = {}
        for coalition_str in miz1.coalition:
            coalition = miz1.coalition[coalition_str]
            for country_str in coalition.countries:
                country = coalition.countries[country_str]
                for plane_group in country.plane_group:
                    if plane_group.has_human():
                        if coalition_str in client_flights:
                            if country_str in client_flights[coalition_str]:
                                client_flights[coalition_str][country_str].append(
                                    plane_group
                                )
                            else:
                                client_flights[coalition_str][country_str] = [
                                    plane_group
                                ]
                        else:
                            client_flights[coalition_str] = {country_str: [plane_group]}
        return client_flights


class MizJoin:
    def __init__(self):
        args = self.parse_args()
        self.miz1_path: Path = args.miz1
        self.miz2_path: Path = args.miz2
        self.miz1 = self.load_miz(args.miz1)
        self.miz2 = self.load_miz(args.miz2)
        self.miz_out = Mission()
        self.miz_out_path = (
            args.output
            if args.output is not None
            else Path(self.miz2_path.parent).joinpath(
                f"{self.miz2_path.stem}_merged.miz"
            )
        )
        # miz1 = Mission.load_file(self.args.miz1)

    def load_miz(self, file_path: Path):
        temp_miz = Mission()
        temp_miz.load_file(file_path)
        return temp_miz

    def merge_client_flights(self):
        self._validate_country_compatibility()
        # TODO: Is this copy really necessary?
        self.miz_out = deepcopy(self.miz2)
        client_flights: ClientFlightCollection = ClientFlight.get_client_flights(
            self.miz1
        )
        for coalition in client_flights:
            for country_str in client_flights[coalition]:
                if country_str not in self.miz_out.coalition[coalition].countries:
                    self.miz_out.coalition[coalition].add_country(
                        country_dict[country_id_from_name(country_str)]()
                    )
                miz_country = self.miz_out.coalition[coalition].countries[country_str]
                client_flights_country = client_flights[coalition][country_str]

                for flying_group in client_flights[coalition][country_str]:
                    miz_country.add_aircraft_group(flying_group)
        self.miz_out.save(self.miz_out_path)

    def _validate_country_compatibility(self):
        blue_countries_1 = list(self.miz1.coalition["blue"].countries)
        red_countries_1 = list(self.miz1.coalition["red"].countries)
        blue_countries_2 = list(self.miz2.coalition["blue"].countries)
        red_countries_2 = list(self.miz2.coalition["red"].countries)
        blue_incompatible_countries = [
            country for country in blue_countries_1 if country in red_countries_2
        ]
        red_incompatible_countries = [
            country for country in red_countries_1 if country in blue_countries_2
        ]
        # TODO: Move this out into an error class
        error_base = "Incompatible countries found between missions.  {} countries in {} found as {} countries in {}"
        if blue_incompatible_countries:
            if red_incompatible_countries:
                raise RuntimeError(
                    str.format(
                        error_base,
                        "Blue",
                        self.miz1_path.name,
                        "red",
                        self.miz2_path.name,
                    )
                    + "\n"
                    + blue_incompatible_countries
                    + "\n\nAND\n\n"
                    + str.format(
                        error_base,
                        "Red",
                        self.miz1_path.name,
                        "blue",
                        self.miz2_path.name,
                    )
                    + "\n"
                    + str(red_incompatible_countries)
                )
            raise RuntimeError(
                str.format(
                    error_base,
                    "Blue",
                    self.miz1_path.name,
                    "red",
                    self.miz2_path.name,
                )
                + "\n"
                + str(blue_incompatible_countries)
            )
        if red_incompatible_countries:
            raise RuntimeError(
                str.format(
                    error_base,
                    "Red",
                    self.miz1_path.name,
                    "blue",
                    self.miz2_path.name,
                )
                + "\n"
                + str(red_incompatible_countries)
            )

    def parse_args(self):
        parser = argparse.ArgumentParser(
            description="Merge client flights from one miz into another"
        )
        parser.add_argument(
            "miz1",
            type=Path,
            help="The .miz file that contains client flights you want to move to another .miz",
        )
        parser.add_argument(
            "miz2",
            type=Path,
            help="The .miz file that you want to move your client flights into",
        )
        parser.add_argument(
            "--output", type=Path, help="Optional custom output file path."
        )
        return parser.parse_args()

def main():
    miz_join = MizJoin()
    miz_join.merge_client_flights()

if __name__ == "__main__":
    main()

