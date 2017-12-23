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
import s from "./AboutSWD.css";
import gql from "graphql-tag";
import { graphql } from "react-apollo";



class AboutSWD extends React.Component {
  static propTypes = {
    
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
       <div>
          <Card>
            
          </Card>
          

        </div>
      </Mobile>
      
    );
  }
}


export default AboutSWD;
