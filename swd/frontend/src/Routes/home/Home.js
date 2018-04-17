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
import MessCard from "./MessCard";
import { Mobile } from "../../Components/Responsive";
import {CardContentLoader} from "../../Components/Loaders";
import InfoCard from "../../Components/InfoCard";
import ExpandableCard from "../../Components/ExpandableCard";
import background from "./Background.svg";
import networkErrorHandler from "./networkErrorHandler";
import bdome from "./BDome.svg";
import s from "./Home.css";
import gql from "graphql-tag";
import { graphql, compose } from "react-apollo";

// GraphQL queries
const userInfoQuery = gql`
  query GetCurrentUser {
    currentUser {
      id
      username
    }
  }
`;
const messCardQuery = gql `
  query messCard($username: String) { 
    messoptionopen{
    openNow,
    month
    }
    messoption(username: $username) {
      mess
    }
  }
  `

const fallback = props => (
    <h1>Something Went Wrong</h1>
);
const loading = props => (
  <h1>Loading...</h1>
);

let MessCardWithData;

class Home extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      // Home currently maintains username state until it is made as context to 
      // be provided to the whole app
      username: null,
    };

  }

  static propTypes = {
    news: PropTypes.arrayOf(
      PropTypes.shape({
        title: PropTypes.string.isRequired,
        link: PropTypes.string.isRequired,
        content: PropTypes.string
      })
    ).isRequired

  };

  componentWillReceiveProps(nextProps)
  {
    if(nextProps.userInfoQuery.currentUser)
    {
    let username = nextProps.userInfoQuery.currentUser.username
    if(username)
    {
      this.setState({ username: username})
    }
    else{
      this.setState({ username: null})
    }
  }
  }

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
this.state.username
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
    );
  }
}

Home.contextTypes = {
  loggedIn: PropTypes.bool,
};

export default graphql(userInfoQuery, {
  name: "userInfoQuery"
}) (Home);


