import React, { Component } from 'react';
import axios from "../axios/axios";


function LoadingMessage() {
    return (
        <div className="splash-screen" style={{
            width: '100 %',
            height: '100 %',
            display: 'flex'
        }}>
            Wait a moment while we load your app 
            <div className="loading-dot">. . . .</div>
        </div>
    );
}

function withSplashScreen(WrappedComponent) {
    return class extends Component {
        constructor(props) {
            super(props);
            this.state = {
                loading1: true,
                loading2: true,
                data: {
                    density: {
                        "type": "FeatureCollection",
                        "features": []
                    }, points: {
                        "type": "FeatureCollection",
                        "features": []
                    }
                }
            };
        }

        componentDidMount() {
            try {
                axios
                    .get("/geojson_density_map", {
                        params: {
                            Bounds: { _sw: { lng: -87.98660192452012, lat: 41.616991663579824}
                                , _ne: { lng: -87.469560248543, lat: 42.073955436739794}}
                        }
                    })
                    .then(({ data }) => {
                        let newData = this.state.data;
                        newData.density = data;
                        this.setState({ data: newData, loading1: false });
                    });

            } catch (err) {
                console.log(err);
                this.setState({
                    loading2: false,
                });
            }
        

            try {
            axios
                .get("/geojson_points_map", {
                    params: {
                        Bounds: {
                            _sw: { lng: -87.98660192452012, lat: 41.616991663579824 }
                            , _ne: { lng: -87.469560248543, lat: 42.073955436739794 }
                        }
                    }
                })
                .then(({ data }) => {
                    let newData = this.state.data;
                    newData.points = data;
                    this.setState({ data: newData, loading2: false });
                });

            } catch (err) {
                console.log(err);
                this.setState({
                    loading2: false,
                });
            }
        }

        render() {
            // while checking user session, show "loading" message
            if (this.state.loading1 || this.state.loading2) return LoadingMessage();
            // otherwise, show the desired route
            return <WrappedComponent data={this.state.data}/>;
        }
    };
}

export default withSplashScreen;