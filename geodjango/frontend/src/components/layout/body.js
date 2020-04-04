// ... other import statements ...
import withSplashScreen from '../splashScreen/splash';
import Mapbox from "../mapbox/mapbox";

// ... App class definition ...

// replace the last line so you pass App as a parameter to withSplashScreen
export default withSplashScreen(Mapbox);