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
                loading: true,
                data: {}
            };
        }

        componentDidMount() {
            try {
                axios
                    //.get("https://chicago-pothole-forecast.herokuapp.com/api/geojson_density_map", {
                    .get("http://127.0.0.1:8000/api/geojson_density_map", {
                        params: {
                            Bounds: { _sw: { lng: -87.98660192452012, lat: 41.616991663579824}
                                , _ne: { lng: -87.469560248543, lat: 42.073955436739794}}
                        }
                    })
                    .then(({ data }) => {
                        this.setState({ data: data, loading: false });
                    });

            } catch (err) {
                console.log(err);
                this.setState({
                    loading: false,
                });
            }
        }

        render() {
            // while checking user session, show "loading" message
            if (this.state.loading) return LoadingMessage();
            // otherwise, show the desired route
            return <WrappedComponent data={this.state.data}/>;
        }
    };
}

export default withSplashScreen;