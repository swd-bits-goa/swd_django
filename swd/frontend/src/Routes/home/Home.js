/* eslint no-unused-vars:0 */

import React from "react";
import PropTypes from "prop-types";
import {
  Card,
  CardActions,
  CardHeader,
  CardMedia,
  CardTitle,
  CardText
} from "material-ui/Card";
import { Mobile } from "../../Components/Responsive";
import InfoCard from "../../Components/InfoCard";
import background from "./Background.svg";
import bdome from "./BDome.svg";
import s from "./Home.css";
import gql from "graphql-tag";
import { graphql } from "react-apollo";

const query = gql`
query GetCurrentUser{
  user(username: "f20110362") {
    username, id
  }
}`

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  componentDidCatch(error, info) {
    // Display fallback UI
    this.setState({ hasError: true });
    // You can also log the error to an error reporting service
    // logErrorToMyService(error, info);
  }

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return <h1>Something went wrong.</h1>;
    }
    return this.props.children;
  }
}

class Home extends React.Component {
  static propTypes = {
    news: PropTypes.arrayOf(
      PropTypes.shape({
        title: PropTypes.string.isRequired,
        link: PropTypes.string.isRequired,
        content: PropTypes.string
      })
    ).isRequired
    // data: PropTypes.shape({
    //   loading: PropTypes.bool,
    //   error: PropTypes.object,
    //   currentUser: PropTypes.object,
    // }).isRequired,
  };

  // const data = (props) => {
  //   const loading = props.data.loading;
  //   const error = props.data.error;
  //   const currentUser = props.data.currentUser;
  //   // render UI with loading, error, or currentUser
  // }

  render() {
    return (
      <Mobile>
        <div
          className={s.container}
          style={{ backgroundImage: `url(${background})` }}
        >
          <Card>
            <CardMedia>
              <img src={bdome} style={{ maxWidth: "80%" }} alt="SWD" />
            </CardMedia>
          </Card>
          <InfoCard title="Latest News" list={this.props.news} />
          {this.props.data && this.props.data.networkStatus === 7 ? (
            <div id="Hello-GQL">{this.props.data.user.username}</div>
          ) : (
            <div>loading</div>
          )}
        </div>
      </Mobile>
    );
  }
}

Home = graphql(query, {
  options: {
    errorPolicy: "all"
  }
})(Home);

export default Home;
