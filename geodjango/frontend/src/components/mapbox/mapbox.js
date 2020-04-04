import React from "react";
import mapboxgl from "mapbox-gl";
import axios from "../axios/axios";
import { debounce } from "lodash";


mapboxgl.accessToken =
  "pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4M29iazA2Z2gycXA4N2pmbDZmangifQ.-g_vE53SD2WrJ6tFX7QHmA";
var bounds = [
  [-87.8166 - 0.2, 41.8305 - 0.2], // Southwest coordinates
  [-87.8166 + 0.3, 41.8305 + 0.1] // Northeast coordinates
];

class Mapbox extends React.Component {
  constructor(props) {
    super(props);
    this.geojson = {};
    this.state = {
      lng: -87.7043,
      lat: 41.8749,
      zoom: 11.02,
      data: {}
    };
  }

  componentDidMount() {
    const { lng, lat, zoom } = this.state;

    const map = new mapboxgl.Map({
      container: this.mapContainer,
      style: "mapbox://styles/mapbox/streets-v11",
      center: [lng, lat],
      zoom,
      maxBounds: "" // Sets bounds as max
    });

    let getBounds = debounce(() => {
      //console.log("The bound is: ", map.getBounds());
    }, 1000);

    map.on("move", () => {
      const { lng, lat } = map.getCenter();
      getBounds();

      this.setState({
        lng: lng.toFixed(4),
        lat: lat.toFixed(4),
        zoom: map.getZoom().toFixed(2)
      });
    });

    map.on("load", () => {
      console.log("map loaded")

      map.addSource("chicago_bound", {
        type: "geojson",
        data: this.props.data
      });
      map.addLayer({
        id: "maine",
        type: "fill",
        source: "chicago_bound",
        layout: {},
        paint: {
          "fill-color": [
            "interpolate",
            ["linear"],
            ["to-number", ["get", "density"]],
            -25,
            "rgba(33,102,172,0)",
            0,
            "rgb(103,169,207)",
            50,
            "rgb(209,229,240)",
            100,
            "rgb(253,219,199)",
            150,
            "rgb(239,138,98)",
            200,
            "rgb(178,24,43)"
          ],
          "fill-opacity": 0.8
        }
      });
 
    });

    // Add geolocate control to the map.
    map.addControl(
      new mapboxgl.GeolocateControl({
        positionOptions: {
          enableHighAccuracy: true
        },
        trackUserLocation: true
      }));
  }

  render() {
    const { lng, lat, zoom } = this.state;

    return (
      <div>
        <div className="inline-block absolute mt12 ml12 bg-darken75 color-white z1 py6 px12 round-full txt-s txt-bold">
          { `Longitude: ${lng} Latitude: ${lat} Zoom: ${zoom}` }
        </div >
        <div
          ref={el => (this.mapContainer = el)}
          className= "Map"
          style={{
            width: '100%',
            height: '92vh',
          }}
        />
      </div>
    );
  }
}

export default Mapbox;
