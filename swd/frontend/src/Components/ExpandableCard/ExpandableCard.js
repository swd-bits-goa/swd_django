import React from 'react';
import PropTypes from 'prop-types';
import {Card, CardActions, CardHeader, CardText} from 'material-ui/Card';
import FlatButton from 'material-ui/FlatButton';
import s from './ExpandableCard.css';

const ExpandableCard = (props) => {

  const { title, text, children } = props;

  return(
<div className={s.container}>
  <Card>
    <CardHeader
      title={title}
      actAsExpander={true}
      showExpandableButton={true}/>
    <CardText expandable={true}>
     {text}
     {children}
    </CardText>
  </Card>
</div>
  );
};

ExpandableCard.propTypes = {
  title: PropTypes.string.isRequired,
  text : PropTypes.string
};

export default ExpandableCard;