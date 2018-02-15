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
// import networkErrorHandler from "./networkErrorHandler";
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


  function networkErrorHandler (LoadingComponent, FallbackComponent,  Component) {
  class NetworkErrorHandler extends React.Component {
    constructor () {
      super()
      // Construct the initial state
      this.state = {
        isLoading: true,
        hasError: false
      }
    }

componentWillReceiveProps() {
      console.log(...this.props, "HoC view of props")
      for (var key in this.props) {
      let query = this.props[key]
      // Need to also consider the case of '!query'
if (query.error) {
// Update state if error happens       
  this.setState({ hasError: true })
  console.log("Error while loading data!")
  console.log(query.error)
} else if (query.loading) {
  this.setState({isLoading: true})
  console.log("Data is loading")
} else {
  this.setState({isLoading: false})
  console.log("Data seems to have loaded")
}
}

      //     if(data.error || !data)
      //     {
      //       // Update state if error happens
      //       this.setState({ hasError: true })
      //     }
          
      // }  
      
    }
    //   // Report errors
    //   errorCallback(error, info, this.props)
   

    render () {
      // if state contains error we render fallback component
      if (this.state.hasError) {
        // Errors can be further split into GraphQL and Network errors
        return (
          <FallbackComponent />
        )
      }
      else if (this.state.isLoading) {
        return (
          <LoadingComponent />
        )
      }
      else {
        return (
        <Component {...this.props} />
        )
      }
    }
  }
  NetworkErrorHandler.displayName = `networkErrorHandler(${Component.displayName})`
  return NetworkErrorHandler
}

const fallback = props => (
    <h1>Something Went Wrong</h1>
);
const loading = props => (
  <h1>Loading...</h1>
);
  // HoC
  let MessCard1 = networkErrorHandler(loading, fallback, MessCard)
const MessCardWithData = compose(
  graphql(messOptionOpenQuery, {
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
})) (MessCard1);


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


