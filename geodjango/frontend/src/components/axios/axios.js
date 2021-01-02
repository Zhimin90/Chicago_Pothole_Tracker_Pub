import axios from "axios";

export default axios.create({
  baseURL: "/api/", //http://127.0.0.1:8000
  responseType: "json"
});
