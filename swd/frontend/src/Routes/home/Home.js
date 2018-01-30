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
import InfoCard from "../../Components/InfoCard";
import ExpandableCard from "../../Components/ExpandableCard";
import background from "./Background.svg";
import bdome from "./BDome.svg";
import s from "./Home.css";
import gql from "graphql-tag";
import { graphql, compose } from "react-apollo";

// All the queries
const userInfoQuery = gql`
  query GetCurrentUser {
    currentUser {
      id
      username
    }
  }
`;

const messOptionOpenQuery = gql`
  query optionOpen { 
    messoptionopen{
    openNow,
    month
    }
  }
  `
const messCurrentChoiceQuery= gql`
query currentChoice {
    currentChoice {
      monthYear,
      mess
    }
  }
  `;

  // HoC
const MessCardWithData = compose(graphql(messOptionOpenQuery, {
  name: "messOptionOpen",
  options: {
    errorPolicy: "all"
  }
}),
graphql(messCurrentChoiceQuery, {
  name: "messCurrentChoice",
  options: {
    errorPolicy: "all"
  }
})) (MessCard);

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

    return (
         <div
          className={s.container}
          >
      <Mobile>
       <div>
        <MessCardWithData/>

          <Card>
            <CardMedia>
              <img src={bdome} style={{ width: "100%" }} alt="SWD" />
            </CardMedia>
          </Card>
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
      </Mobile>
      </div>
    );
  }
}

export default graphql(userInfoQuery, {
  name: "userInfoQuery",
  options: {
    errorPolicy: "all"
  }
}) (Home);


