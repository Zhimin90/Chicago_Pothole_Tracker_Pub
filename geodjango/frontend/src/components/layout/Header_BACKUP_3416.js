import React, { Component } from "react";
<<<<<<< HEAD
import Mapbox from "../mapbox/mapbox";
=======
>>>>>>> 5a064a302ab95bdf045a41796cb89de6fff2fe53

export class Header extends Component {
  render() {
    return (
<<<<<<< HEAD
      <div>
        <nav className="navbar navbar-expand-sm navbar-light bg-light">
          <button
            className="navbar-toggler"
            type="button"
            data-toggle="collapse"
            data-target="#navbarTogglerDemo01"
            aria-controls="navbarTogglerDemo01"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarTogglerDemo01">
            <a className="navbar-brand" href="#">
              Django React App
            </a>
            <ul className="navbar-nav mr-auto mt-2 mt-lg-0"></ul>
          </div>
        </nav>
        <Mapbox />
      </div>
=======
      <nav className="navbar navbar-expand-sm navbar-light bg-light">
        <button
          className="navbar-toggler"
          type="button"
          data-toggle="collapse"
          data-target="#navbarTogglerDemo01"
          aria-controls="navbarTogglerDemo01"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarTogglerDemo01">
          <a className="navbar-brand" href="#">
            Django React App
          </a>
          <ul className="navbar-nav mr-auto mt-2 mt-lg-0"></ul>
        </div>
      </nav>
>>>>>>> 5a064a302ab95bdf045a41796cb89de6fff2fe53
    );
  }
}

export default Header;
