import os

from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for
)

from dotenv import load_dotenv

from database import get_db_connection


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)


# =========================================================
# SECRET KEY
# =========================================================

app.secret_key = os.getenv(
    "SECRET_KEY"
)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# TEST DATABASE
# =========================================================

@app.route("/test-db")
def test_db():

    try:

        connection = get_db_connection()

        if connection.is_connected():

            connection.close()

            return "MySQL connection successful!"

        return "MySQL connection failed!"

    except Exception as e:

        return f"Database error: {e}"


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        location = request.form["location"]
        bio = request.form["bio"]

        try:

            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO users
                (
                    name,
                    email,
                    password,
                    location,
                    bio
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    name,
                    email,
                    password,
                    location,
                    bio
                )
            )

            connection.commit()

            cursor.close()
            connection.close()

            return "Registration successful! Your account was saved."

        except Exception as e:

            return f"Registration failed: {e}"

    return render_template("register.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        try:

            connection = get_db_connection()

            cursor = connection.cursor(
                dictionary=True
            )

            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE email = %s
                AND password = %s
                """,
                (
                    email,
                    password
                )
            )

            user = cursor.fetchone()

            cursor.close()
            connection.close()


            if user:

                session["user_id"] = user["user_id"]

                session["user_name"] = user["name"]

                session["user_location"] = user["location"]

                return redirect(
                    url_for("dashboard")
                )


            return "Invalid email or password."


        except Exception as e:

            return f"Login failed: {e}"


    return render_template("login.html")


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(url_for("login"))

    current_user_id = session["user_id"]


    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute(
            """
            SELECT
                user_id,
                name,
                email,
                location,
                bio

            FROM users

            WHERE user_id = %s
            """,
            (current_user_id,)
        )

        user = cursor.fetchone()


        cursor.execute(
            """
            SELECT COUNT(*) AS total

            FROM user_offers

            WHERE user_id = %s
            """,
            (current_user_id,)
        )

        offer_count = cursor.fetchone()["total"]


        cursor.execute(
            """
            SELECT COUNT(*) AS total

            FROM user_needs

            WHERE user_id = %s
            """,
            (current_user_id,)
        )

        need_count = cursor.fetchone()["total"]


        cursor.execute(
            """
            SELECT COUNT(*) AS total

            FROM exchange_requests

            WHERE
            (
                sender_id = %s
                OR receiver_id = %s
            )

            AND status = 'ACCEPTED'
            """,
            (
                current_user_id,
                current_user_id
            )
        )

        exchange_count = cursor.fetchone()["total"]


        cursor.execute(
            """
            SELECT
                COUNT(*) AS review_count,
                COALESCE(
                    AVG(rating),
                    0
                ) AS average_rating

            FROM reviews

            WHERE reviewee_id = %s
            """,
            (current_user_id,)
        )

        rating_data = cursor.fetchone()


        review_count = rating_data["review_count"]

        average_rating = float(
            rating_data["average_rating"]
        )


        cursor.close()
        connection.close()


        return render_template(
            "dashboard.html",
            user=user,
            offer_count=offer_count,
            need_count=need_count,
            exchange_count=exchange_count,
            review_count=review_count,
            average_rating=average_rating
        )


    except Exception as e:

        return f"Could not load dashboard: {e}"


# =========================================================
# PROFILE
# =========================================================

@app.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    current_user_id = session["user_id"]


    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        if request.method == "POST":

            teach_skills = request.form.getlist(
                "teach_skills"
            )

            provide_services = request.form.getlist(
                "provide_services"
            )

            learn_skills = request.form.getlist(
                "learn_skills"
            )

            need_services = request.form.getlist(
                "need_services"
            )


            cursor.execute(
                """
                DELETE FROM user_offers

                WHERE user_id = %s
                """,
                (current_user_id,)
            )


            cursor.execute(
                """
                DELETE FROM user_needs

                WHERE user_id = %s
                """,
                (current_user_id,)
            )


            offers = (
                [
                    (item, "SKILL")
                    for item in teach_skills
                ]
                +
                [
                    (item, "SERVICE")
                    for item in provide_services
                ]
            )


            for item, offer_type in offers:

                cursor.execute(
                    """
                    SELECT skill_id

                    FROM skills

                    WHERE skill_name = %s
                    """,
                    (item,)
                )

                result = cursor.fetchone()


                if result:

                    cursor.execute(
                        """
                        INSERT INTO user_offers
                        (
                            user_id,
                            skill_id,
                            offer_type
                        )
                        VALUES
                        (
                            %s,
                            %s,
                            %s
                        )
                        """,
                        (
                            current_user_id,
                            result["skill_id"],
                            offer_type
                        )
                    )


            needs = (
                [
                    (item, "SKILL")
                    for item in learn_skills
                ]
                +
                [
                    (item, "SERVICE")
                    for item in need_services
                ]
            )


            for item, need_type in needs:

                cursor.execute(
                    """
                    SELECT skill_id

                    FROM skills

                    WHERE skill_name = %s
                    """,
                    (item,)
                )

                result = cursor.fetchone()


                if result:

                    cursor.execute(
                        """
                        INSERT INTO user_needs
                        (
                            user_id,
                            skill_id,
                            need_type
                        )
                        VALUES
                        (
                            %s,
                            %s,
                            %s
                        )
                        """,
                        (
                            current_user_id,
                            result["skill_id"],
                            need_type
                        )
                    )


            connection.commit()


        # Get user

        cursor.execute(
            """
            SELECT
                user_id,
                name,
                email,
                location,
                bio

            FROM users

            WHERE user_id = %s
            """,
            (current_user_id,)
        )

        user = cursor.fetchone()


        # Get offers

        cursor.execute(
            """
            SELECT
                skills.skill_name,
                user_offers.offer_type

            FROM user_offers

            JOIN skills

            ON user_offers.skill_id =
               skills.skill_id

            WHERE user_offers.user_id = %s
            """,
            (current_user_id,)
        )

        offers = cursor.fetchall()


        teach_skills = []

        provide_services = []


        for offer in offers:

            if offer["offer_type"] == "SKILL":

                teach_skills.append(
                    offer["skill_name"]
                )

            else:

                provide_services.append(
                    offer["skill_name"]
                )


        # Get needs

        cursor.execute(
            """
            SELECT
                skills.skill_name,
                user_needs.need_type

            FROM user_needs

            JOIN skills

            ON user_needs.skill_id =
               skills.skill_id

            WHERE user_needs.user_id = %s
            """,
            (current_user_id,)
        )

        needs = cursor.fetchall()


        learn_skills = []

        need_services = []


        for need in needs:

            if need["need_type"] == "SKILL":

                learn_skills.append(
                    need["skill_name"]
                )

            else:

                need_services.append(
                    need["skill_name"]
                )


        # Rating

        cursor.execute(
            """
            SELECT
                COUNT(*) AS review_count,

                COALESCE(
                    AVG(rating),
                    0
                ) AS average_rating

            FROM reviews

            WHERE reviewee_id = %s
            """,
            (current_user_id,)
        )

        rating_data = cursor.fetchone()


        review_count = rating_data["review_count"]

        average_rating = float(
            rating_data["average_rating"]
        )


        cursor.close()

        connection.close()


        return render_template(
            "profile.html",

            user=user,

            teach_skills=teach_skills,

            provide_services=provide_services,

            learn_skills=learn_skills,

            need_services=need_services,

            review_count=review_count,

            average_rating=average_rating
        )


    except Exception as e:

        return f"Could not load profile: {e}"


# =========================================================
# PUBLIC USER PROFILE
# =========================================================

@app.route(
    "/user/<int:user_id>"
)
def user_profile(user_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    current_user_id = session["user_id"]


    if user_id == current_user_id:

        return redirect(
            url_for("profile")
        )


    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute(
            """
            SELECT
                user_id,
                name,
                email,
                location,
                bio

            FROM users

            WHERE user_id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()


        if not user:

            cursor.close()

            connection.close()

            return "User not found."


        cursor.execute(
            """
            SELECT
                skills.skill_name,
                user_offers.offer_type

            FROM user_offers

            JOIN skills

            ON user_offers.skill_id =
               skills.skill_id

            WHERE user_offers.user_id = %s

            ORDER BY skills.skill_name
            """,
            (user_id,)
        )

        offers = cursor.fetchall()


        teach_skills = []

        provide_services = []


        for offer in offers:

            if offer["offer_type"] == "SKILL":

                teach_skills.append(
                    offer["skill_name"]
                )

            else:

                provide_services.append(
                    offer["skill_name"]
                )


        cursor.execute(
            """
            SELECT
                skills.skill_name,
                user_needs.need_type

            FROM user_needs

            JOIN skills

            ON user_needs.skill_id =
               skills.skill_id

            WHERE user_needs.user_id = %s

            ORDER BY skills.skill_name
            """,
            (user_id,)
        )

        needs = cursor.fetchall()


        learn_skills = []

        need_services = []


        for need in needs:

            if need["need_type"] == "SKILL":

                learn_skills.append(
                    need["skill_name"]
                )

            else:

                need_services.append(
                    need["skill_name"]
                )


        offer_count = len(offers)

        need_count = len(needs)


        cursor.execute(
            """
            SELECT COUNT(*) AS total

            FROM exchange_requests

            WHERE
            (
                sender_id = %s
                OR receiver_id = %s
            )

            AND status = 'COMPLETED'
            """,
            (
                user_id,
                user_id
            )
        )

        completed_exchanges = cursor.fetchone()["total"]


        cursor.execute(
            """
            SELECT
                COUNT(*) AS review_count,

                COALESCE(
                    AVG(rating),
                    0
                ) AS average_rating

            FROM reviews

            WHERE reviewee_id = %s
            """,
            (user_id,)
        )

        rating_data = cursor.fetchone()


        review_count = rating_data["review_count"]

        average_rating = float(
            rating_data["average_rating"]
        )


        cursor.execute(
            """
            SELECT
                reviews.rating,
                reviews.comment,
                reviews.created_at,
                users.name AS reviewer_name

            FROM reviews

            JOIN users

            ON reviews.reviewer_id =
               users.user_id

            WHERE reviews.reviewee_id = %s

            ORDER BY reviews.created_at DESC

            LIMIT 5
            """,
            (user_id,)
        )

        reviews = cursor.fetchall()


        cursor.close()

        connection.close()


        return render_template(
            "user_profile.html",

            user=user,

            teach_skills=teach_skills,

            provide_services=provide_services,

            learn_skills=learn_skills,

            need_services=need_services,

            offer_count=offer_count,

            need_count=need_count,

            completed_exchanges=completed_exchanges,

            review_count=review_count,

            average_rating=average_rating,

            reviews=reviews
        )


    except Exception as e:

        return f"Could not load user profile: {e}"


# =========================================================
# MATCHES
# =========================================================

@app.route("/matches")
def matches():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    current_user_id = session["user_id"]


    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        # ------------------------------------------------
        # All offers
        # ------------------------------------------------

        cursor.execute(
            """
            SELECT
                user_offers.user_id,
                user_offers.skill_id,
                user_offers.offer_type,
                skills.skill_name

            FROM user_offers

            JOIN skills

            ON user_offers.skill_id =
               skills.skill_id
            """
        )

        all_offers = cursor.fetchall()


        # ------------------------------------------------
        # All needs
        # ------------------------------------------------

        cursor.execute(
            """
            SELECT
                user_needs.user_id,
                user_needs.skill_id,
                user_needs.need_type,
                skills.skill_name

            FROM user_needs

            JOIN skills

            ON user_needs.skill_id =
               skills.skill_id
            """
        )

        all_needs = cursor.fetchall()


        # ------------------------------------------------
        # All other users
        # ------------------------------------------------

        cursor.execute(
            """
            SELECT
                user_id,
                name,
                location,
                bio

            FROM users

            WHERE user_id != %s
            """,
            (current_user_id,)
        )

        users = cursor.fetchall()


        # ------------------------------------------------
        # Current user's data
        # ------------------------------------------------

        current_offers = set()

        current_needs = set()


        for offer in all_offers:

            if offer["user_id"] == current_user_id:

                current_offers.add(
                    (
                        offer["skill_id"],
                        offer["offer_type"]
                    )
                )


        for need in all_needs:

            if need["user_id"] == current_user_id:

                current_needs.add(
                    (
                        need["skill_id"],
                        need["need_type"]
                    )
                )


        # Skill names

        skill_names = {}


        for offer in all_offers:

            skill_names[
                offer["skill_id"]
            ] = offer["skill_name"]


        for need in all_needs:

            skill_names[
                need["skill_id"]
            ] = need["skill_name"]


        match_results = []


        # =================================================
        # MATCH EACH USER
        # =================================================

        for user in users:

            candidate_id = user["user_id"]

            candidate_offers = set()

            candidate_needs = set()


            for offer in all_offers:

                if offer["user_id"] == candidate_id:

                    candidate_offers.add(
                        (
                            offer["skill_id"],
                            offer["offer_type"]
                        )
                    )


            for need in all_needs:

                if need["user_id"] == candidate_id:

                    candidate_needs.add(
                        (
                            need["skill_id"],
                            need["need_type"]
                        )
                    )


            my_need_matches = (
                current_needs &
                candidate_offers
            )


            my_offer_matches = (
                current_offers &
                candidate_needs
            )


            if (
                not my_need_matches
                and
                not my_offer_matches
            ):

                continue


            # ------------------------------------------------
            # Score
            # ------------------------------------------------

            score = 0


            if my_need_matches:

                score += 50


            if my_offer_matches:

                score += 30


            if (
                user["location"]
                and
                session.get("user_location")

                and

                user["location"].lower()
                ==
                session.get("user_location").lower()
            ):

                score += 20


            score = min(
                score,
                100
            )


            if (
                my_need_matches
                and
                my_offer_matches
            ):

                match_type = "Mutual Match"

            else:

                match_type = "Compatible Match"


            # ------------------------------------------------
            # Get request status
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT status

                FROM exchange_requests

                WHERE sender_id = %s

                AND receiver_id = %s

                ORDER BY request_id DESC

                LIMIT 1
                """,
                (
                    current_user_id,
                    candidate_id
                )
            )


            request_result = cursor.fetchone()


            if request_result:

                request_status = request_result["status"]

            else:

                request_status = None


            # ------------------------------------------------
            # Matched skills
            # ------------------------------------------------

            needs_matched = []


            for skill_id, item_type in my_need_matches:

                needs_matched.append(
                    skill_names.get(
                        skill_id,
                        "Unknown"
                    )
                )


            offers_matched = []


            for skill_id, item_type in my_offer_matches:

                offers_matched.append(
                    skill_names.get(
                        skill_id,
                        "Unknown"
                    )
                )


            match_results.append(
                {
                    "user_id":
                        candidate_id,

                    "name":
                        user["name"],

                    "location":
                        user["location"],

                    "bio":
                        user["bio"],

                    "score":
                        score,

                    "match_type":
                        match_type,

                    "needs_matched":
                        needs_matched,

                    "offers_matched":
                        offers_matched,

                    "request_status":
                        request_status
                }
            )


        match_results.sort(
            key=lambda x: x["score"],
            reverse=True
        )


        return render_template(
            "matches.html",
            matches=match_results
        )


    except Exception as e:

        return f"Matching failed: {e}"


# =========================================================
# SEND REQUEST
# =========================================================

@app.route(
    "/send-request",
    methods=["POST"]
)
def send_request():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    sender_id = session["user_id"]

    receiver_id = request.form["receiver_id"]


    try:

        connection = get_db_connection()

        cursor = connection.cursor()


        # Check latest request

        cursor.execute(
            """
            SELECT
                request_id,
                status

            FROM exchange_requests

            WHERE sender_id = %s

            AND receiver_id = %s

            ORDER BY request_id DESC

            LIMIT 1
            """,
            (
                sender_id,
                receiver_id
            )
        )


        existing_request = cursor.fetchone()


        if (
            existing_request
            and
            existing_request[1] in (
                "PENDING",
                "ACCEPTED"
            )
        ):

            cursor.close()

            connection.close()

            return redirect(
                url_for("matches")
            )


        cursor.execute(
            """
            INSERT INTO exchange_requests
            (
                sender_id,
                receiver_id,
                status
            )

            VALUES
            (
                %s,
                %s,
                'PENDING'
            )
            """,
            (
                sender_id,
                receiver_id
            )
        )


        connection.commit()

        cursor.close()

        connection.close()


        return redirect(
            url_for("matches")
        )


    except Exception as e:

        return f"Request failed: {e}"


# =========================================================
# REQUESTS
# =========================================================

@app.route("/requests")
def my_requests():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    current_user_id = session["user_id"]


    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        # Incoming

        cursor.execute(
            """
            SELECT
                exchange_requests.request_id,
                exchange_requests.status,
                users.name,
                users.location,
                users.bio

            FROM exchange_requests

            JOIN users

            ON exchange_requests.sender_id =
               users.user_id

            WHERE
                exchange_requests.receiver_id = %s

            ORDER BY
                exchange_requests.created_at DESC
            """,
            (current_user_id,)
        )


        incoming = cursor.fetchall()


        # Outgoing

        cursor.execute(
            """
            SELECT
                exchange_requests.request_id,
                exchange_requests.status,
                users.name

            FROM exchange_requests

            JOIN users

            ON exchange_requests.receiver_id =
               users.user_id

            WHERE
                exchange_requests.sender_id = %s

            ORDER BY
                exchange_requests.created_at DESC
            """,
            (current_user_id,)
        )


        outgoing = cursor.fetchall()


        cursor.close()

        connection.close()


        return render_template(
            "requests.html",

            incoming=incoming,

            outgoing=outgoing
        )


    except Exception as e:

        return f"Could not load requests: {e}"


# =========================================================
# ACCEPT REQUEST
# =========================================================

@app.route(
    "/accept-request",
    methods=["POST"]
)
def accept_request():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    request_id = request.form["request_id"]

    current_user_id = session["user_id"]


    try:

        connection = get_db_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            UPDATE exchange_requests

            SET status = 'ACCEPTED'

            WHERE request_id = %s

            AND receiver_id = %s
            """,
            (
                request_id,
                current_user_id
            )
        )


        connection.commit()

        cursor.close()

        connection.close()


        return redirect(
            url_for("my_requests")
        )


    except Exception as e:

        return f"Accept failed: {e}"


# =========================================================
# REJECT REQUEST
# =========================================================

@app.route(
    "/reject-request",
    methods=["POST"]
)
def reject_request():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    request_id = request.form["request_id"]

    current_user_id = session["user_id"]


    try:

        connection = get_db_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            UPDATE exchange_requests

            SET status = 'REJECTED'

            WHERE request_id = %s

            AND receiver_id = %s
            """,
            (
                request_id,
                current_user_id
            )
        )


        connection.commit()

        cursor.close()

        connection.close()


        return redirect(
            url_for("my_requests")
        )


    except Exception as e:

        return f"Reject failed: {e}"


# =========================================================
# SCHEDULE
# =========================================================

@app.route(
    "/schedule/<int:request_id>",
    methods=["GET", "POST"]
)
def schedule_exchange(request_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    current_user_id = session["user_id"]


    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute(
            """
            SELECT
                request_id,
                sender_id,
                receiver_id,
                status

            FROM exchange_requests

            WHERE request_id = %s

            AND (
                sender_id = %s

                OR receiver_id = %s
            )
            """,
            (
                request_id,
                current_user_id,
                current_user_id
            )
        )


        exchange_request = cursor.fetchone()


        if not exchange_request:

            cursor.close()

            connection.close()

            return "Exchange request not found."


        if exchange_request["status"] not in (
            "ACCEPTED",
            "COMPLETED"
        ):

            cursor.close()

            connection.close()

            return "This request is not ready for exchange."


        cursor.execute(
            """
            SELECT *

            FROM exchange_sessions

            WHERE request_id = %s
            """,
            (request_id,)
        )


        existing_session = cursor.fetchone()


        if existing_session:

            cursor.close()

            connection.close()

            return redirect(
                url_for(
                    "exchange_session",
                    request_id=request_id
                )
            )


        if request.method == "POST":

            date = request.form["date"]

            time = request.form["time"]

            mode = request.form["mode"]


            cursor.execute(
                """
                INSERT INTO exchange_sessions
                (
                    request_id,
                    date,
                    time,
                    mode,
                    status
                )

                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    'SCHEDULED'
                )
                """,
                (
                    request_id,
                    date,
                    time,
                    mode
                )
            )


            connection.commit()

            cursor.close()

            connection.close()


            return redirect(
                url_for(
                    "exchange_session",
                    request_id=request_id
                )
            )


        cursor.close()

        connection.close()


        return render_template(
            "schedule.html",
            request=exchange_request
        )


    except Exception as e:

        return f"Scheduling failed: {e}"


# =========================================================
# VIEW EXCHANGE
# =========================================================

@app.route(
    "/exchange/<int:request_id>"
)
def exchange_session(request_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    current_user_id = session["user_id"]


    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute(
            """
            SELECT
                es.session_id,
                es.request_id,
                es.date,
                es.time,
                es.mode,
                es.status,

                er.sender_id,
                er.receiver_id

            FROM exchange_sessions es

            JOIN exchange_requests er

            ON es.request_id =
               er.request_id

            WHERE es.request_id = %s

            AND (
                er.sender_id = %s

                OR er.receiver_id = %s
            )

            ORDER BY
                es.session_id DESC

            LIMIT 1
            """,
            (
                request_id,
                current_user_id,
                current_user_id
            )
        )


        session_data = cursor.fetchone()


        cursor.close()

        connection.close()


        if not session_data:

            return "No exchange session found."


        return render_template(
            "exchange.html",
            session_data=session_data
        )


    except Exception as e:

        return f"Could not load exchange: {e}"


# =========================================================
# COMPLETE EXCHANGE
# =========================================================

@app.route(
    "/complete-exchange",
    methods=["POST"]
)
def complete_exchange():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    session_id = request.form["session_id"]

    request_id = request.form["request_id"]

    current_user_id = session["user_id"]


    try:

        connection = get_db_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            UPDATE exchange_sessions es

            JOIN exchange_requests er

            ON es.request_id =
               er.request_id

            SET es.status = 'COMPLETED'

            WHERE es.session_id = %s

            AND es.request_id = %s

            AND (
                er.sender_id = %s

                OR er.receiver_id = %s
            )
            """,
            (
                session_id,
                request_id,
                current_user_id,
                current_user_id
            )
        )


        cursor.execute(
            """
            UPDATE exchange_requests

            SET status = 'COMPLETED'

            WHERE request_id = %s

            AND (
                sender_id = %s

                OR receiver_id = %s
            )
            """,
            (
                request_id,
                current_user_id,
                current_user_id
            )
        )


        connection.commit()

        cursor.close()

        connection.close()


        return redirect(
            url_for(
                "review_exchange",
                session_id=session_id
            )
        )


    except Exception as e:

        return f"Could not complete exchange: {e}"


# =========================================================
# REVIEW
# =========================================================

@app.route(
    "/review/<int:session_id>",
    methods=["GET", "POST"]
)
def review_exchange(session_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    current_user_id = session["user_id"]


    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute(
            """
            SELECT
                es.session_id,
                es.status,

                er.sender_id,
                er.receiver_id,

                sender.name AS sender_name,

                receiver.name AS receiver_name

            FROM exchange_sessions es

            JOIN exchange_requests er

            ON es.request_id =
               er.request_id

            JOIN users sender

            ON er.sender_id =
               sender.user_id

            JOIN users receiver

            ON er.receiver_id =
               receiver.user_id

            WHERE es.session_id = %s

            AND (
                er.sender_id = %s

                OR er.receiver_id = %s
            )
            """,
            (
                session_id,
                current_user_id,
                current_user_id
            )
        )


        exchange = cursor.fetchone()


        if not exchange:

            cursor.close()

            connection.close()

            return "Exchange not found."


        if current_user_id == exchange["sender_id"]:

            reviewee_id = exchange["receiver_id"]

            reviewee_name = exchange["receiver_name"]

        else:

            reviewee_id = exchange["sender_id"]

            reviewee_name = exchange["sender_name"]


        if request.method == "POST":

            rating = int(
                request.form["rating"]
            )

            comment = request.form.get(
                "comment",
                ""
            )


            if rating < 1 or rating > 5:

                cursor.close()

                connection.close()

                return "Rating must be between 1 and 5."


            cursor.execute(
                """
                SELECT review_id

                FROM reviews

                WHERE session_id = %s

                AND reviewer_id = %s
                """,
                (
                    session_id,
                    current_user_id
                )
            )


            existing_review = cursor.fetchone()


            if existing_review:

                cursor.close()

                connection.close()

                return redirect(
                    url_for("dashboard")
                )


            cursor.execute(
                """
                INSERT INTO reviews
                (
                    session_id,
                    reviewer_id,
                    reviewee_id,
                    rating,
                    comment
                )

                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    session_id,
                    current_user_id,
                    reviewee_id,
                    rating,
                    comment
                )
            )


            connection.commit()

            cursor.close()

            connection.close()


            return redirect(
                url_for("dashboard")
            )


        cursor.close()

        connection.close()


        return render_template(
            "review.html",

            exchange=exchange,

            reviewee_name=reviewee_name
        )


    except Exception as e:

        return f"Could not load review: {e}"


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )