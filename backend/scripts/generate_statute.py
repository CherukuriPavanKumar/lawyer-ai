import json
import os

data = [
    {
        "section_number": "2",
        "title": "Interpretation-clause",
        "text": "In this Act the following words and expressions are used in the following senses, unless a contrary intention appears from the context: (a) When one person signifies to another his willingness to do or to abstain from doing anything, with a view to obtaining the assent of that other to such act or abstinence, he is said to make a proposal; (b) When the person to whom the proposal is made signifies his assent thereto, the proposal is said to be accepted. A proposal, when accepted, becomes a promise; (d) When, at the desire of the promisor, the promisee or any other person has done or abstained from doing, or does or abstains from doing, or promises to do or to abstain from doing, something, such act or abstinence or promise is called a consideration for the promise;"
    },
    {
        "section_number": "10",
        "title": "What agreements are contracts",
        "text": "All agreements are contracts if they are made by the free consent of parties competent to contract, for a lawful consideration and with a lawful object, and are not hereby expressly declared to be void. Nothing herein contained shall affect any law in force in India, and not hereby expressly repealed, by which any contract is required to be made in writing or in the presence of witnesses, or any law relating to the registration of documents."
    },
    {
        "section_number": "11",
        "title": "Who are competent to contract",
        "text": "Every person is competent to contract who is of the age of majority according to the law to which he is subject, and who is of sound mind, and is not disqualified from contracting by any law to which he is subject."
    },
    {
        "section_number": "13",
        "title": "Consent defined",
        "text": "Two or more persons are said to consent when they agree upon the same thing in the same sense."
    },
    {
        "section_number": "14",
        "title": "Free consent defined",
        "text": "Consent is said to be free when it is not caused by - (1) coercion, as defined in section 15, or (2) undue influence, as defined in section 16, or (3) fraud, as defined in section 17, or (4) misrepresentation, as defined in section 18, or (5) mistake, subject to the provisions of sections 20, 21 and 22. Consent is said to be so caused when it would not have been given but for the existence of such coercion, undue influence, fraud, misrepresentation or mistake."
    },
    {
        "section_number": "15",
        "title": "Coercion defined",
        "text": "Coercion is the committing, or threatening to commit, any act forbidden by the Indian Penal Code (45 of 1860) or the unlawful detaining, or threatening to detain, any property, to the prejudice of any person whatever, with the intention of causing any person to enter into an agreement."
    },
    {
        "section_number": "16",
        "title": "Undue influence defined",
        "text": "(1) A contract is said to be induced by undue influence where the relations subsisting between the parties are such that one of the parties is in a position to dominate the will of the other and uses that position to obtain an unfair advantage over the other. (2) In particular and without prejudice to the generality of the foregoing principle, a person is deemed to be in a position to dominate the will of another - (a) where he holds a real or apparent authority over the other, or where he stands in a fiduciary relation to the other; or (b) where he makes a contract with a person whose mental capacity is temporarily or permanently affected by reason of age, illness, or mental or bodily distress."
    },
    {
        "section_number": "17",
        "title": "Fraud defined",
        "text": "Fraud means and includes any of the following acts committed by a party to a contract, or with his connivance, or by his agent, with intent to deceive another party thereto or his agent, or to induce him to enter into the contract: (1) the suggestion, as a fact, of that which is not true, by one who does not believe it to be true; (2) the active concealment of a fact by one having knowledge or belief of the fact; (3) a promise made without any intention of performing it; (4) any other act fitted to deceive; (5) any such act or omission as the law specially declares to be fraudulent."
    },
    {
        "section_number": "18",
        "title": "Misrepresentation defined",
        "text": "Misrepresentation means and includes - (1) the positive assertion, in a manner not warranted by the information of the person making it, of that which is not true, though he believes it to be true; (2) any breach of duty which, without an intent to deceive, gains an advantage to the person committing it, or any one claiming under him; by misleading another to his prejudice or to the prejudice of any one claiming under him; (3) causing, however innocently, a party to an agreement to make a mistake as to the substance of the thing which is the subject of the agreement."
    },
    {
        "section_number": "23",
        "title": "What considerations and objects are lawful and what not",
        "text": "The consideration or object of an agreement is lawful, unless - it is forbidden by law; or is of such a nature that, if permitted, it would defeat the provisions of any law; or is fraudulent; or involves or implies injury to the person or property of another; or the Court regards it as immoral, or opposed to public policy. In each of these cases, the consideration or object of an agreement is said to be unlawful. Every agreement of which the object or consideration is unlawful is void."
    },
    {
        "section_number": "24",
        "title": "Agreements void, if considerations and objects unlawful in part",
        "text": "If any part of a single consideration for one or more objects, or any one or any part of any one of several considerations for a single object, is unlawful, the agreement is void."
    },
    {
        "section_number": "25",
        "title": "Agreement without consideration, void, unless it is in writing and registered",
        "text": "An agreement made without consideration is void, unless - (1) it is expressed in writing and registered under the law for the time being in force for the registration of documents, and is made on account of natural love and affection between parties standing in a near relation to each other; or unless (2) it is a promise to compensate, wholly or in part, a person who has already voluntarily done something for the promisor, or something which the promisor was legally compellable to do; or unless (3) it is a promise, made in writing and signed by the person to be charged therewith, or by his agent generally or specially authorized in that behalf, to pay wholly or in part a debt of which the creditor might have enforced payment but for the law for the limitation of suits. In any of these cases, such an agreement is a contract."
    },
    {
        "section_number": "73",
        "title": "Compensation for loss or damage caused by breach of contract",
        "text": "When a contract has been broken, the party who suffers by such breach is entitled to receive, from the party who has broken the contract, compensation for any loss or damage caused to him thereby, which naturally arose in the usual course of things from such breach, or which the parties knew, when they made the contract, to be likely to result from the breach of it. Such compensation is not to be given for any remote and indirect loss or damage sustained by reason of the breach."
    },
    {
        "section_number": "74",
        "title": "Compensation for breach of contract where penalty stipulated for",
        "text": "When a contract has been broken, if a sum is named in the contract as the amount to be paid in case of such breach, or if the contract contains any other stipulation by way of penalty, the party complaining of the breach is entitled, whether or not actual damage or loss is proved to have been caused thereby, to receive from the party who has broken the contract reasonable compensation not exceeding the amount so named or, as the case may be, the penalty stipulated for."
    }
]

def main():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'statutes')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'contract_act_1872.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Created dummy statute data with {len(data)} sections at {out_path}")

if __name__ == '__main__':
    main()
