import React, { Component } from "react";
import Splash from "./body"

export class Header extends Component {
  render() {
    return (
      <div>
        <nav className="navbar navbar-expand-sm navbar-light bg-light">
          <div className="collapse navbar-collapse" id="navbarTogglerDemo01">
            <a className="navbar-brand" href="">
              Chicago Pothole Forecast
            </a>
            <ul className="navbar-nav mr-auto mt-2 mt-lg-0"></ul>
          </div>
        </nav>
        <Splash />
        <div className="d-flex justify-content-center">
          <ul className="nav text-center">
            <li className="nav-item text-center">
              <a className="nav-link disabled text-center" href="#">Built with Mapbox GL, TensorFlow, GeoDjango, and Geopandas</a>
            </li>
            <li className="nav-item text-center">
              <a className="nav-link text-center" href="https://github.com/Zhimin90/Chicago_Pothole_Tracker_Pub">Github</a>
            </li>
            <li className="nav-item text-center">
              <a className="nav-link text-center" href="https://zhiminsportfolio.herokuapp.com/home">MyPortfolio</a>
            </li>
          </ul>
        </div>
      </div>
    );
  }
}

export default Header;
