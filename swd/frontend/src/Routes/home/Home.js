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
import {CardContentLoader} from "../../Components/Loaders";
import InfoCard from "../../Components/InfoCard";
import background from "./Background.svg";
import bdome from "./BDome.svg";
import s from "./Home.css";
import gql from "graphql-tag";
import { graphql } from "react-apollo";

const query = gql`
  query GetCurrentUser {
    currentUser {
      id
      username
    }
  }
`;

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

  };
  render() {

  // HoC
 MessCardWithData = compose(
graphql(messCardQuery, {
  name: "messOption",
options : {
  variables: {
     username: this.state.username
  }
}
}))(networkErrorHandler(CardContentLoader, fallback, MessCard));
    

    return (
         <div
          className={s.container}
        >
{
this.context.loggedIn
  ? <MessCardWithData/>
  : null
}
{
  !this.context.loggedIn
  ? (
            <div className={s.imgContainer}>
                 <img src={bdome} style={{ width: "100%"}} alt="BITS Pilani, KK Birla Goa Campus" />
                <div className={s.bottomleft}>BITS Pilani, Goa Campus</div>
            </div>
  )
  : null
}
            <div className={s.container2}>
              <InfoCard title="Latest News" list={this.props.news} />
              {/* TODO: Handle apollo errors */}
              {this.props.userInfoQuery && this.props.userInfoQuery.networkStatus === 7 ? (
                <div>
                  {this.props.userInfoQuery.currentUser &&
                    this.props.userInfoQuery.currentUser.username}
                </div>
              ) : (
                <div>loading</div>
              )}
            </div>
        </div>
      </Mobile>
      </div>
    );
  }
}

Home = graphql(query, {
  options: {
    errorPolicy: "all"
  }
})(Home);

export default Home;
