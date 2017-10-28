const { HashRouter, Link, Switch, Route } = ReactRouterDOM;

const ownerUserData = {
  ownerUser: "mayank",
  images: [
    {
      id: 0,
      url:
        "https://images.pexels.com/photos/190819/pexels-photo-190819.jpeg?h=350&w=350&auto=compress&cs=tinysrgb",
      likes: 2,
      like: ["mayank", "dave"],
      comments: [
        { mayank: "Nice image" },
        { dave: "Great watch" },
        { mayank: "Nice image again" },
        { dennis: "Beautiful bezel" }
      ],
      fav: ["dennis", "dave"]
    },
    {
      id: 1,
      url:
        "https://images.pexels.com/photos/9352/glass-time-watch-business.jpg?h=350&w=350&auto=compress&cs=tinysrgb",
      likes: 3,
      like: ["mayank", "dave", "dennis"],
      comments: [
        { dave: "Great watch" },
        { mayank: "Nice image again" },
        { dennis: "Beautiful bezel" }
      ],
      fav: ["dennis"]
    },
    {
      id: 2,
      url:
        "https://images.pexels.com/photos/552598/pexels-photo-552598.jpeg?h=350&w=350&auto=compress&cs=tinysrgb",
      likes: 2,
      like: ["mayank", "dave"],
      comments: [
        { mayank: "Nice image" },
        { dave: "Great watch" },
        { mayank: "Nice image again" },
        { dennis: "Beautiful bezel" }
      ],
      fav: ["dennis", "dave"]
    },
    {
      id: 3,
      url:
        "https://images.pexels.com/photos/236900/pexels-photo-236900.jpeg?h=350&w=350&auto=compress&cs=tinysrgb",
      likes: 2,
      like: ["mayank", "dave"],
      comments: [
        { mayank: "Nice image" },
        { dave: "Great watch" },
        { mayank: "Nice image again" },
        { dennis: "Beautiful bezel" }
      ],
      fav: ["dennis", "dave"]
    },
    {
      id: 4,
      url:
        "https://images.pexels.com/photos/280250/pexels-photo-280250.jpeg?h=350&w=350&auto=compress&cs=tinysrgb",
      likes: 2,
      like: ["mayank", "dave"],
      comments: [
        { mayank: "Nice image" },
        { dave: "Great watch" },
        { mayank: "Nice image again" },
        { dennis: "Beautiful bezel" }
      ],
      fav: ["dennis", "dave"]
    },
    {
      id: 5,
      url:
        "https://images.pexels.com/photos/8592/pexels-photo.jpg?h=350&w=350&auto=compress&cs=tinysrgb",
      likes: 2,
      like: ["mayank", "dave"],
      comments: [
        { mayank: "Nice image" },
        { dave: "Great watch" },
        { mayank: "Nice image again" },
        { dennis: "Beautiful bezel" }
      ],
      fav: ["dennis", "dave"]
    }
  ]
};

const GetComments = comm => {
  let key = Object.keys(comm)[0];
  let val = Object.values(comm)[0];

  return (
    <li>
      <a href="#" id="comment-user"><span>{key}</span></a>
      <span id="comment">{val}</span>
    </li>
  );
};

class Comments extends React.Component {
  constructor(props) {
    super(props);
    this.state = { value: "" };
    this.handleChange = this.handleChange.bind(this);
  }

  handleChange(e) {
    this.setState({ value: e.target.value });
  }

  render() {
    return (
      <section className="comment-section">
        <section className="row text-left">
          <section className="col-md-12">
            <ul id="comments">
              {this.props.comments.map(com => {
                return GetComments(com);
              })}
            </ul>
          </section>
        </section>
        <br />
        <section className="row text-left">
          <section className="col-md-10">
            <input
              type="text"
              className="form-control"
              id="usr-comment"
              value={this.state.value}
              onChange={this.handleChange}
            />
          </section>
          <section className="col-md-2">
            <a href="javascript:void(0)" id="add-comment">
              <i
                className="fa fa-plus-circle"
                aria-hidden="true"
                onClick={e => {
                  const val = this.state.value;
                  this.setState({ value: "" });
                  this.props.onHandleComment(val);
                }}
              />
            </a>
          </section>
        </section>
      </section>
    );
  }
}

// TODO: think of having this component
// it's own state instead of in MetaPanel
class LikeUnlike extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <section className="row text-left">
        <section className="col-md-12">
          <ul id="like-unlike" className="align-middle">
            <li>
              <a href="javascript:void(0)" id="thumbs-up">
                <i
                  className={
                    this.props.likeUnlike === true
                      ? "fa fa-thumbs-up"
                      : "fa fa-thumbs-o-up"
                  }
                  aria-hidden="true"
                  onClick={e => this.props.onHandleLikeUnlike(e)}
                />
              </a>
            </li>
            <li>
              <a href="javascript:void(0)" id="fav">
                <i
                  className={
                    this.props.fav === true ? "fa fa-heart" : "fa fa-heart-o"
                  }
                  aria-hidden="true"
                  onClick={e => this.props.onHandleLikeUnlike(e)}
                />
              </a>
            </li>
            <li><span>{this.props.likes} likes</span></li>
          </ul>
        </section>
      </section>
    );
  }
}

const UserName = props => {
  return (
    <section className="row">
      <section className="col-md-6 text-left">
        <h3>{props.ownerUserName}</h3>
      </section>
    </section>
  );
};

// TODO:
// Update state object. Remove the keys
// which are not needed in the state
// Move the state to individual {} if
// it leads to better design and perf.
class MetaPanel extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      id: "",
      ownerUser: "",
      currentUser: "",
      likes: 0,
      like: [],
      comments: [],
      fav: []
    };

    this.handleLikeUnlike = this.handleLikeUnlike.bind(this);
    this.handleComment = this.handleComment.bind(this);
  }

  componentDidMount() {
    const prop = this.props.image_meta;
    if (this.props.id === prop.id) {
      this.setState({
        id: prop.id,
        ownerUser: this.props.ownerUser,
        currentUser: this.props.currentUser,
        likes: prop.likes,
        like: prop.like,
        comments: prop.comments,
        fav: prop.fav
      });
    } else {
      this.setState({ ownerUser: this.props.ownerUser });
    }
  }

  handleLikeUnlike(e) {
    const target = e.target.className;
    if (target.indexOf("thumbs") !== -1) {
      if (target.indexOf("thumbs-up") !== -1) {
        let like = this.state.like;
        let likeUsers = like.slice(like.indexOf(this.state.currentUser), 0);
        this.setState(prevState => {
          return {
            like: likeUsers,
            likes: prevState.likes - 1
          };
        });
      } else if (target.indexOf("thumbs-o-up") !== -1) {
        let like = this.state.like;
        like.push(this.state.currentUser);
        this.setState(prevState => {
          return {
            like: like,
            likes: prevState.likes + 1
          };
        });
      }
    } else if (target.indexOf("heart") !== -1) {
      if (target.indexOf("fa-heart-o") !== -1) {
        let favs = this.state.fav;
        favs.push(this.state.currentUser);
        this.setState({ fav: favs });
      } else if (target.indexOf("fa-heart") !== -1) {
        let favs = this.state.fav;
        let newFavs = favs.slice(favs.indexOf(this.state.currentUser), 0);
        this.setState({ fav: newFavs });
      }
    }
  }

  handleComment(e) {
    const comment = this.state.comments;
    const currentUser = this.state.currentUser;
    comment.push({ [currentUser]: e });
    this.setState({ comments: comment });
  }

  render() {
    // prop.like.indexOf(this.props.currentUser) !== -1 ? true : false
    // prop.fav.indexOf(this.props.currentUser) !== -1 ? true : false
    const user = this.state.ownerUser,
      likeUnlike = this.state.like.indexOf(this.state.currentUser) !== -1
        ? true
        : false,
      likes = this.state.likes,
      comments = this.state.comments,
      currentUser = this.state.currentUser,
      fav = this.state.fav.indexOf(this.state.currentUser) !== -1
        ? true
        : false;

    return (
      <div className="col-md-4">
        <UserName ownerUserName={user} /> {<hr />}
        <LikeUnlike
          likeUnlike={likeUnlike}
          likes={likes}
          fav={fav}
          onHandleLikeUnlike={this.handleLikeUnlike}
        />
        {" "}{<hr />}
        <Comments comments={comments} onHandleComment={this.handleComment} />
      </div>
    );
  }
}

const ImagePanel = img => {
  // const img = parseInt(props.match.params.id);
  let finalUrl = ownerUserData["images"][img].url.replace(/350/g, "700");

  return <img src={finalUrl} />;
};

const Image = props => {
  const id = props.match.params.id;
  const imgId = parseInt(id);
  return (
    <div className="container">
      <br />
      <div className="row">
        <div className="col-md-8">
          {ImagePanel(imgId)}
        </div>
        <MetaPanel
          image_meta={ownerUserData["images"][imgId]}
          id={imgId}
          ownerUser={ownerUserData["ownerUser"]}
          currentUser="dennis"
        />
      </div>
    </div>
  );
};

const AllImages = () => {
  const ownerUserImgs = ownerUserData["images"];
  const noOfImages = ownerUserImgs.length;
  let count = 0,
    block = [],
    rows = [];

  const _renderRow = block => {
    return (
      <div className="row">
        {block}
      </div>
    );
  };

  const _renderRows = () => {
    for (let i = 0; i < noOfImages; i++) {
      block.push(
        <div className="col-md-4">
          <Link to={`/${ownerUserImgs[i].id}`}>
            <img src={`${ownerUserImgs[i].url}`} />
          </Link>
        </div>
      );
      if (block.length >= 3) {
        const row = _renderRow(block);
        if (row) {
          rows.push(row);
          rows.push(<br />);
        }
        block = [];
      }
    }
    const row = _renderRow(block);
    if (row) {
      rows.push(row);
    }

    return rows;
  };
  return (
    <div className="container">
      <br />
      {_renderRows()}
    </div>
  );
};

const Main = () => {
  return (
    <main>
      <Switch>
        <Route exact path="/" component={AllImages} />
        <Route path="/:id" component={Image} />
      </Switch>
    </main>
  );
};

const Header = () => {
  return (
    <section>
      <h1 className="text-center text-muted">
        <span className="label label-default">ShareIt</span>
      </h1>
      <div className="text-center">
        <h4>This is an Instragram clone written in React.js</h4>
      </div>
    </section>
  );
};

const App = () => {
  return (
    <div>
      <Header />
      <Main />
    </div>
  );
};

ReactDOM.render(
  <HashRouter>
    <App />
  </HashRouter>,
  document.getElementById("root")
);

/* --- like-unlike --- */
    var newsrc = "mars.jpg";
    if ( newsrc == "mars.jpg" ) {
    function thumbUp() {
        document.getElementById("thumbUp").innerHTML = "Hello World";
    }


var newsrc = "mars.jpg";

function changeImage() {
  if ( newsrc == "mars.jpg" ) {
    document.images["pic"].src = "/images/program/js/forms/mars.jpg";
    document.images["pic"].alt = "Mars";
    newsrc  = "earth.jpg";
  }
  else {
    document.images["pic"].src = "/images/program/js/forms/earth.jpg";
    document.images["pic"].alt = "Earth";
    newsrc  = "mars.jpg";
  }
}



  <img src="../static/thumb-up.png" id="thumbUp" onclick="thumbUp()">
  <img src="../static/thumb-up-active.png" id="thumbUp-active" hidden onclick="thumbUp()">